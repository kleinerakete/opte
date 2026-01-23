defmodule PuzscanPhoenixWeb.StorageController do
  use PuzscanPhoenixWeb, :controller

  def get_pdf(conn, %{"key" => key}) do
    bucket = System.get_env("S3_BUCKET") || ""
    # Generate presigned URL via ExAws if configured
    url =
      try do
        {:ok, presigned} = ExAws.S3.presigned_url(ExAws.Config.new(:s3), :get, bucket, key)
        presigned
      rescue
        _ -> ""
      end

    if url != "" do
      redirect(conn, external: url)
    else
      conn |> put_status(404) |> json(%{error: "not found"})
    end
  end
end
