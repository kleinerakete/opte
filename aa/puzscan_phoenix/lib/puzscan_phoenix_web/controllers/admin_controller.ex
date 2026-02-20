defmodule PuzscanPhoenixWeb.AdminController do
  use PuzscanPhoenixWeb, :controller

  @admin_secret System.get_env("ADMIN_SECRET") || "changeme"

  def auth(conn, %{"secret" => secret}) do
    if secret == @admin_secret do
      json(conn, %{ok: true})
    else
      conn |> put_status(401) |> json(%{ok: false})
    end
  end

  def update_weights(conn, _params) do
    secret = get_req_header(conn, "x-admin-secret") |> List.first()
    if secret != @admin_secret do
      conn |> put_status(401) |> json(%{ok: false, error: "unauthorized"})
    else
      body = read_body!(conn)
      case Jason.decode(body) do
        {:ok, payload} ->
          dir = System.get_env("PUZ_DB_DIR") || "./db"
          File.mkdir_p!(dir)
          path = Path.join(dir, "weights.json")
          payload = Map.merge(payload, %{"_ts" => DateTime.utc_now() |> DateTime.to_iso8601()})
          File.write!(path, Jason.encode!(payload))
          json(conn, %{ok: true})
        _ ->
          conn |> put_status(400) |> json(%{ok: false, error: "invalid json"})
      end
    end
  end

  defp read_body!(conn) do
    {:ok, body, _} = Plug.Conn.read_body(conn)
    body
  end
end
