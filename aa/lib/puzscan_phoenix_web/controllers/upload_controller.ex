defmodule PuzscanPhoenixWeb.UploadController do
  use PuzscanPhoenixWeb, :controller
  alias PuzscanPhoenix.Jobs
  require Logger

  def upload(conn, %{"file" => %Plug.Upload{filename: filename, path: path}, "email" => email, "metadata" => metadata}) do
    {:ok, bin} = File.read(path)
    bucket = System.get_env("S3_BUCKET") || ""
    key = "uploads/" <> UUID.uuid4() <> "_" <> filename

    # Upload to S3 via external API call to python worker or ExAws; here we proxy to Python worker upload endpoint if configured
    python_upload = System.get_env("PY_WORKER_HTTP_UPLOAD")
    if python_upload && python_upload != "" do
      # forward binary to python upload endpoint
      headers = [{"Content-Type", "application/octet-stream"}, {"x-filename", filename}]
      HTTPoison.post!(python_upload, bin, headers, params: %{"key" => key})
    else
      # fallback: leave key, expect python worker can fetch from shared storage
      :ok
    end

    job = Jobs.create_job(%{job_id: UUID.uuid4(), s3_key: key, email: email, metadata: metadata, status: "queued"})
    Oban.insert!(%Oban.Job{queue: :default, worker: PuzscanPhoenix.Workers.ProcessJob, args: %{s3_key: key, metadata: metadata, email: email, job_id: job.job_id}})
    json(conn, %{status: "queued", job_id: job.job_id})
  rescue
    e ->
      Logger.error("upload error: #{inspect(e)}")
      conn |> put_status(500) |> json(%{error: "upload failed"})
  end

  def upload(conn, _params) do
    conn |> put_status(400) |> json(%{error: "invalid payload"})
  end
end
