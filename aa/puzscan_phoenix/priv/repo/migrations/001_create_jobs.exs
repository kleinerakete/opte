defmodule PuzscanPhoenix.Repo.Migrations.CreateJobs do
  use Ecto.Migration

  def change do
    create table(:jobs, primary_key: false) do
      add :id, :binary_id, primary_key: true
      add :job_id, :string
      add :s3_key, :string
      add :pdf_key, :string
      add :ei, :float
      add :v, :float
      add :r, :float
      add :f, :float
      add :s, :float
      add :metadata, :map
      add :status, :string
      timestamps()
    end

    create index(:jobs, [:job_id])
  end
end
