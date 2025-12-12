import Config

config :puzscan_phoenix, PuzscanPhoenix.Repo,
  username: "postgres",
  password: "postgres",
  database: "puzscan_dev",
  hostname: "localhost",
  show_sensitive_data_on_connection_error: true,
  pool_size: 10

config :puzscan_phoenix, PuzscanPhoenixWeb.Endpoint,
  http: [ip: {0,0,0,0}, port: 4000],
  debug_errors: true,
  code_reloader: true,
  check_origin: false,
  watchers: []
