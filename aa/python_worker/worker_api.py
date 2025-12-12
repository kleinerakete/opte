from fastapi import FastAPI, Request
import os, json, base64, requests, time
from analysis import compute_V, compute_R, compute_F, compute_S, compute_ei, preprocess_image_bytes
import boto3

app = FastAPI()
S3_BUCKET = os.getenv('S3_BUCKET')
PHOENIX_CALLBACK = os.getenv('PHOENIX_CALLBACK_URL')  # e.g. http://phoenix:4000/api/jobs/complete
PHOENIX_API_KEY = os.getenv('PHOENIX_API_KEY')

# simple endpoint that receives job payload {s3_key, metadata, email, job_id, s3_fetch_url optional}
@app.post('/process')
async def process(request: Request):
    payload = await request.json()
    s3_key = payload.get('s3_key')
    metadata = payload.get('metadata','{}')
    job_id = payload.get('job_id')
    s3_fetch_url = payload.get('s3_fetch_url')  # optional pre-signed url
    # fetch image from S3
    s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION'))
    if s3_fetch_url:
        import requests as r
        resp = r.get(s3_fetch_url)
        img_bytes = resp.content
    else:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        img_bytes = obj['Body'].read()
    # compute metrics
    V = compute_V(img_bytes)
    R = compute_R(img_bytes)
    F = compute_F(img_bytes)
    S = compute_S(metadata)
    EI, comps = compute_ei(V,R,F,S)
    # generate basic pdf (very simple) - here we create a text pdf via weasyprint
    from jinja2 import Template
    from weasyprint import HTML
    tpl = Template(open('report_template.html').read())
    html = tpl.render(title='Puz19 Report', metrics={'V':V,'R':R,'F':F,'S':S,'EI':EI}, text='Automated analysis')
    pdf_bytes = HTML(string=html).write_pdf()
    # upload PDF to S3
    key = f"reports/{job_id}.pdf"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=pdf_bytes, ContentType='application/pdf')
    # callback to Phoenix to mark job complete
    if PHOENIX_CALLBACK:
        headers = {'Content-Type': 'application/json', 'x-api-key': PHOENIX_API_KEY}
        cb = {'job_id': job_id, 'pdf_key': key, 'ei': EI, 'v': V, 'r': R, 'f': F, 's': S}
        try:
            requests.post(PHOENIX_CALLBACK, json=cb, timeout=10, headers=headers)
        except Exception as e:
            print('Callback failed', e)
    return {'status':'done', 'pdf_key': key, 'ei': EI}
