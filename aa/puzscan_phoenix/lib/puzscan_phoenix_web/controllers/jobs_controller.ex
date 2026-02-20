defmodule PuzscanPhoenixWeb.JobsController do
  use PuzscanPhoenixWeb, :controller
  alias PuzscanPhoenix.Jobs
  @api_key System.get_env("PHOENIX_API_KEY")

  def complete(conn, params) do
    # check header key
    key = get_req_header(conn, "x-api-key") |> List.first()
    if key != @api_key do
      conn |> put_status(401) |> json(%{ok: false, error: "unauthorized"})
    else
      job_id = params["job_id"]
      pdf_key = params["pdf_key"]
      ei = params["ei"] |> parse_float()
      v = params["v"] |> parse_float()
      r = params["r"] |> parse_float()
      f = params["f"] |> parse_float()
      s = params["s"] |> parse_float()
      case Jobs.get_job_by_job_id(job_id) do
        nil -> conn |> put_status(404) |> json(%{ok: false, error: "job not found"})
        job ->
          {:ok, _} = PuzscanPhoenix.Repo.update(Ecto.Changeset.change(job, %{status: "done", pdf_key: pdf_key, ei: ei, v: v, r: r, f: f, s: s}))
          json(conn, %{ok: true})
      end
    end
  end

  defp parse_float(nil), do: nil
  defp parse_float(x) when is_float(x), do: x
  defp parse_float(x) when is_binary(x), do: String.to_float(x)
  defp parse_float(_), do: nil
end
