defmodule PuzscanPhoenixWeb.StatusController do
  use PuzscanPhoenixWeb, :controller
  alias PuzscanPhoenix.Jobs

  def status(conn, %{"job_id" => job_id}) do
    case Jobs.get_job_by_job_id(job_id) do
      nil -> json(conn, %{status: "not_found"})
      job -> json(conn, %{status: job.status, pdf_key: job.pdf_key, EI: job.ei})
    end
  end

  def status(conn, _params) do
    conn |> put_status(400) |> json(%{error: "job_id required"})
  end
end
