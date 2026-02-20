defmodule PuzscanPhoenixWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :puzscan_phoenix

  plug Plug.RequestId
  plug Plug.Logger
  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Plug.MethodOverride
  plug Plug.Head
  plug PuzscanPhoenixWeb.Router
end
