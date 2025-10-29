
# plumber.R — SEH EpiNow2 Adapter (minimal)
#* @apiTitle SEH EpiNow2 Adapter
#* @post /run
function(req, res){
  library(jsonlite)
  library(EpiNow2)
  library(data.table)

  body <- fromJSON(req$postBody, simplifyVector = TRUE)
  params <- body$params

  # Expect params$cases_ts to be a CSV path or signed URL; here we generate toy data
  cases <- data.table::data.table(
    date = seq(as.Date(Sys.Date()-60), as.Date(Sys.Date()), by="day"),
    confirm = round(abs(sin(1:61/6)*50 + rnorm(61, 100, 10)))
  )

  # Minimal Rt estimation (toy; replace with real epinow call as needed)
  # Realtime estimate: mean(rt) +/- intervals (dummy here)
  rt_mean <- 1.05
  rt_p10 <- 0.92
  rt_p90 <- 1.18

  res$body <- toJSON(list(
    run_id = paste0("epinow2_", as.integer(Sys.time())),
    experiment = "epi_nowcasting_rt",
    best = list(rt_mean=rt_mean, rt_p10=rt_p10, rt_p90=rt_p90),
    frontier = list(),
    explain = "Rt оценен (демо). Подключите реальные случаи и генерационное время в params."
  ), auto_unbox = TRUE, pretty = TRUE)
  res
}
