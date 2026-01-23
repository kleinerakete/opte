# General application configuration
import Config

config :puzscan_phoenix,
  ecto_repos: [PuzscanPhoenix.Repo]

config :puzscan_phoenix, PuzscanPhoenix.Repo,
  database: System.get_env("PG_DB") || "puzscan_dev",
  username: System.get_env("PG_USER") || "postgres",
  password: System.get_env("PG_PASS") || "postgres",
  hostname: System.get_env("PG_HOST") || "localhost",
  pool_size: 10

config :puzscan_phoenix, Oban,
  repo: PuzscanPhoenix.Repo,
  queues: [default: 10],
  plugins: [Oban.Plugins.Pruner]

config :ex_aws,
  access_key_id: [{:system, "AWS_ACCESS_KEY_ID"}, :instance_role],
  secret_access_key: [{:system, "AWS_SECRET_ACCESS_KEY"}, :instance_role],
  region: System.get_env("AWS_REGION") || "eu-central-1"

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]
