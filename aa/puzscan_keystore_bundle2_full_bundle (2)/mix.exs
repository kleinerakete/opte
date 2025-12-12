defmodule PuzscanPhoenix.MixProject do
  use Mix.Project

  def project do
    [
      app: :puzscan_phoenix,
      version: "0.1.0",
      elixir: "~> 1.15",
      elixirc_paths: elixirc_paths(Mix.env()),
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      mod: {PuzscanPhoenix.Application, []},
      extra_applications: [:logger, :runtime_tools, :os_mon]
    ]
  end

  defp elixirc_paths(_), do: ["lib"]

  defp deps do
    [
      {:phoenix, "~> 1.7.7"},
      {:phoenix_pubsub, "~> 2.1"},
      {:phoenix_ecto, "~> 4.4"},
      {:ecto_sql, "~> 3.10"},
      {:postgrex, ">= 0.0.0"},
      {:oban, "~> 2.14"},
      {:ex_aws, "~> 2.3"},
      {:ex_aws_s3, "~> 2.3"},
      {:sweet_xml, "~> 0.7"},
      {:hackney, "~> 1.18"},
      {:jason, "~> 1.4"},
      {:plug_cowboy, "~> 2.6"},
      {:uuid, "~> 1.1"},
      {:httpoison, "~> 1.8"}
    ]
  end
end
