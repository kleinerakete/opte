defmodule PuzscanPhoenixWeb.Router do
  use PuzscanPhoenixWeb, :router

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", PuzscanPhoenixWeb do
    pipe_through :api

    post "/upload", UploadController, :upload
    get "/status", StatusController, :status
    post "/admin/auth", AdminController, :auth
    post "/admin/update-weights", AdminController, :update_weights
    get "/storage/:key", StorageController, :get_pdf
  end
end
