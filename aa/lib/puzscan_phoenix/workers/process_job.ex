defmodule PuzscanPhoenix.Workers.ProcessJob do
  use Oban.Worker, queue: :default, max_attempts: 5
  require Logger

  def perform(%Oban.Job{args: %{"s3_key" => s3_key, "metadata" => metadata, "email" => email, "job_id" => job_id}}) do
    # Call external Python worker HTTP endpoint if configured
    api = System.get_env("PY_WORKER_HTTP") || ""
    if api != "" do
      url = api <> "/process"
      body = Jason.encode!(%{s3_key: s3_key, metadata: metadata, email: email, job_id: job_id})
      headers = [{"Content-Type", "application/json"}]
      case HTTPoison.post(url, body, headers, []) do
        {:ok, resp} ->
          Logger.info("Called python worker: #{inspect(resp.status_code)}")
        {:error, err} ->
          Logger.error("Error calling python worker: #{inspect(err)}")
      end
    else
      Logger.warn("No PY_WORKER_HTTP configured; job left for external worker to pick up")
    end
    :ok
  end
end
