import io, os, json, math, numpy as np
from PIL import Image, ImageFilter
import imagehash, cv2
from scipy.spatial.distance import cosine
import hashlib

DB_DIR = os.getenv('PUZ_DB_DIR','./db')

def load_json(name):
    path = os.path.join(DB_DIR, name)
    if not os.path.exists(path):
        return {}
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

PHASH_DB = load_json('phashes.json')
LINES_DB = load_json('lines.json')
PART_DB = load_json('particles.json')
TAG_DB = load_json('tags.json')

def preprocess_image_bytes(img_bytes, max_side=1024):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    width, height = img.size
    ratio = min(1.0, max_side/float(max(width,height)))
    if ratio < 1.0:
        img = img.resize((int(width*ratio), int(height*ratio)), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.2))
    return img

def phash_of_image(img_pil):
    return imagehash.phash(img_pil)

def hamming_similarity(hash1, hash2):
    if not hash1 or not hash2:
        return 0.0
    if isinstance(hash1, str):
        h1 = imagehash.hex_to_hash(hash1).hash
    else:
        h1 = hash1.hash
    if isinstance(hash2, str):
        h2 = imagehash.hex_to_hash(hash2).hash
    else:
        h2 = hash2.hash
    dist = (h1 != h2).sum()
    length = h1.size
    sim = 1.0 - (dist/float(length))
    return float(max(0.0, min(1.0, sim)))

def compute_V(img_bytes):
    img = preprocess_image_bytes(img_bytes)
    ph = phash_of_image(img)
    if not PHASH_DB:
        return 0.5
    best = 0.0
    for k,v in PHASH_DB.items():
        sim = hamming_similarity(ph, v)
        if sim > best:
            best = sim
    return float(best)

def detect_lines(img_pil):
    img = np.array(img_pil.convert('L'))
    edges = cv2.Canny(img,50,150,apertureSize=3)
    kernel = np.ones((3,3),np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=60, minLineLength=30, maxLineGap=10)
    res = []
    if lines is None:
        return res
    h,w = img.shape[:2]
    for l in lines:
        x1,y1,x2,y2 = l[0]
        res.append([x1/w, y1/h, x2/w, y2/h])
    return res

def line_vector_features(line):
    x1,y1,x2,y2 = line
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    angle_norm = (angle + math.pi)/(2*math.pi)
    cx = (x1 + x2)/2.0
    cy = (y1 + y2)/2.0
    length = math.hypot(dx, dy)
    return np.array([angle_norm, cx, cy, length])

def lines_similarity(linesA, linesB):
    if not linesA or not linesB:
        return 0.0
    featsA = [line_vector_features(l) for l in linesA]
    featsB = [line_vector_features(l) for l in linesB]
    A = np.array(featsA)
    B = np.array(featsB)
    dists = []
    for a in A:
        d = np.linalg.norm(B - a, axis=1)
        dists.append(d.min())
    mean_dist = float(np.mean(dists))
    max_possible = math.sqrt(4.0)
    sim = 1.0 - (mean_dist / max_possible)
    return float(max(0.0, min(1.0, sim)))

def compute_R(img_bytes):
    img = preprocess_image_bytes(img_bytes)
    lines = detect_lines(img)
    if not LINES_DB:
        return 0.5
    best = 0.0
    for k, lines_ref in LINES_DB.items():
        sim = lines_similarity(lines, lines_ref)
        if sim > best:
            best = sim
    return float(best)

def detect_blobs(img_pil):
    img = np.array(img_pil.convert('L'))
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 5
    params.maxArea = 50000
    detector = cv2.SimpleBlobDetector_create(params)
    kps = detector.detect(img)
    sizes = [kp.size for kp in kps]
    return sizes

def histogram_from_sizes(sizes, bins=12, range_max=200):
    if not sizes:
        return np.zeros(bins, dtype=float)
    hist, _ = np.histogram(sizes, bins=bins, range=(0, range_max))
    if hist.sum() > 0:
        hist = hist.astype(float)/hist.sum()
    return hist

def compute_F(img_bytes):
    img = preprocess_image_bytes(img_bytes)
    sizes = detect_blobs(img)
    hist = histogram_from_sizes(sizes, bins=12, range_max=200)
    if not PART_DB:
        return 0.5
    best = 0.0
    for k, ref_hist in PART_DB.items():
        ref = np.array(ref_hist, dtype=float)
        try:
            sim = 1.0 - cosine(hist, ref)
        except:
            sim = 0.0
        if math.isnan(sim):
            sim = 0.0
        if sim > best:
            best = float(sim)
    return float(max(0.0, min(1.0, best)))

STOPWORDS = set(["und","oder","der","die","das","ein","eine","in","auf","mit","von","zu","für","ist","als","auch"]) 
def normalize_tags(metadata_str):
    try:
        obj = json.loads(metadata_str)
        tags = []
        if isinstance(obj, dict) and "tags" in obj:
            tags = obj.get("tags") or []
        elif isinstance(obj, list):
            tags = obj
        else:
            tags = [str(obj)]
    except Exception:
        tags = [t.strip().lower() for t in metadata_str.replace(","," ").split() if t.strip()]
    norm = []
    for t in tags:
        if not isinstance(t, str): continue
        s = t.lower().strip()
        s = ''.join(ch for ch in s if ch.isalnum() or ch==' ')
        if s in STOPWORDS or len(s) < 2: continue
        norm.append(s)
    return list(dict.fromkeys(norm))

def jaccard_similarity(a,b):
    if not a or not b: return 0.0
    sa=set(a); sb=set(b)
    inter = sa.intersection(sb)
    uni = sa.union(sb)
    return float(len(inter)/len(uni)) if uni else 0.0

def compute_S(metadata_str):
    tags = normalize_tags(metadata_str)
    if not TAG_DB:
        return 0.5
    best = 0.0
    for k, ref_tags in TAG_DB.items():
        sim = jaccard_similarity(tags, ref_tags)
        if sim > best:
            best = sim
    return float(best)

def compute_ei(V,R,F,S, weights=(0.35,0.30,0.20,0.15)):
    wV,wR,wF,wS = weights
    raw = wV*(1.0 - V) + wR*(1.0 - R) + wF*(1.0 - F) + wS*(1.0 - S)
    norm = max(0.0, min(1.0, (raw - 0.0)/(1.0 - 0.0)))
    EI = norm * 10.0
    return EI, {'raw': raw, 'norm': norm, 'weights': weights}
