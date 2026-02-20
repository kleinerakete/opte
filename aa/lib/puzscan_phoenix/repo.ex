defmodule PuzscanPhoenix.Repo do
  use Ecto.Repo,
    otp_app: :puzscan_phoenix,
    adapter: Ecto.Adapters.Postgres
end
