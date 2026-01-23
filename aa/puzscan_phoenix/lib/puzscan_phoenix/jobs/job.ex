defmodule PuzscanPhoenix.Jobs.Job do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:id, :binary_id, autogenerate: true}
  schema "jobs" do
    field :job_id, :string
    field :s3_key, :string
    field :pdf_key, :string
    field :ei, :float
    field :v, :float
    field :r, :float
    field :f, :float
    field :s, :float
    field :metadata, :map
    field :status, :string
    timestamps()
  end

  def changeset(job, attrs) do
    job
    |> cast(attrs, [:job_id, :s3_key, :pdf_key, :ei, :v, :r, :f, :s, :metadata, :status])
    |> validate_required([:job_id, :s3_key, :status])
  end
end
