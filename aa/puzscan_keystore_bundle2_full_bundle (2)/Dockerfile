FROM elixir:1.15.4-erlang-25.3-alpine AS build
WORKDIR /app
RUN apk add --no-cache build-base npm git
COPY mix.exs mix.lock ./
RUN mix local.hex --force && mix local.rebar --force
RUN mix deps.get
COPY . .
RUN mix compile

FROM elixir:1.15.4-erlang-25.3-alpine
WORKDIR /app
COPY --from=build /app /app
EXPOSE 4000
CMD ["mix", "phx.server"]
