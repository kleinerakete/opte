defmodule PuzscanPhoenix.Application do
  @moduledoc false
  use Application

  def start(_type, _args) do
    children = [
      PuzscanPhoenix.Repo,
      {Phoenix.PubSub, name: PuzscanPhoenix.PubSub},
      PuzscanPhoenixWeb.Endpoint,
      {Oban, Application.fetch_env!(:puzscan_phoenix, Oban)}
    ]

    opts = [strategy: :one_for_one, name: PuzscanPhoenix.Supervisor]
    Supervisor.start_link(children, opts)
  end

  def config_change(changed, _new, removed) do
    PuzscanPhoenixWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
