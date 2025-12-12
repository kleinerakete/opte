defmodule PuzscanPhoenix.Jobs do
  import Ecto.Query, warn: false
  alias PuzscanPhoenix.Repo
  alias PuzscanPhoenix.Jobs.Job

  def create_job(attrs) do
    %Job{}
    |> Job.changeset(attrs)
    |> Repo.insert!()
  end

  def get_job_by_job_id(job_id) do
    Repo.get_by(Job, job_id: job_id)
  end
end
