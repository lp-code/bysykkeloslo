setwd("C:/Users/sraoul/Documents/Hackathon/Bike_Prediction/trips_csv/data/interim")
Base <- read.csv("trips.csv", sep=",")
backup <- Base
Base <- backup

##########################################################Part 1###########################################################################
Base$Start.station <- as.factor(Base$Start.station)
Base$End.station <- as.factor(Base$End.station)
Base$Start.time <- as.POSIXct(Base$Start.time)
Base$End.time <- as.POSIXct(Base$End.time)


Base[,which(colnames(Base)=="DurationSeconds") + 1: +10] <- data.frame(year_start = as.numeric(format(Base$Start.time, format = "%Y")),
                                                                      month_start = as.numeric(format(Base$Start.time, format = "%m")),
                                                                      day_start = as.numeric(format(Base$Start.time, format = "%d")),
                                                                      hour_start = as.numeric(format(Base$Start.time, format =  "%H")),
                                                                      minute_start = as.numeric(format(Base$Start.time, format =  "%M")),
                                                                      year_end = as.numeric(format(Base$End.time, format = "%Y")),
                                                                      month_end = as.numeric(format(Base$End.time, format = "%m")),
                                                                      day_end = as.numeric(format(Base$End.time, format = "%d")),
                                                                      hour_end = as.numeric(format(Base$End.time, format =  "%H")),
                                                                      minute_end = as.numeric(format(Base$End.time, format =  "%M")))


########################################################################################################################################
interval <- as.numeric(seq(5, 60, by = 5))
Base_test <- Base[min(which(Base$month_start == 9 & Base$year_start == 2018)):max(which(Base$month_start == 8 & Base$year_start == 2018)),]

Base_test$time_int_start <- Base_test$time_int_end <- c(NA)

Base_test$time_int_start <- ifelse(Base_test$minute_start < 5, 0, Base_test$time_int_start)
Base_test$time_int_end <- ifelse(Base_test$minute_end < 5, 0, Base_test$time_int_end)


for(i in 1:11)
{
  Base_test$time_int_start <- ifelse(Base_test$minute_start >= interval[i] & Base_test$minute_start < interval[i+1], 
                                     interval[i], Base_test$time_int_start)
  Base_test$time_int_end <- ifelse(Base_test$minute_end >= interval[i] & Base_test$minute_end < interval[i+1], 
                                   interval[i], Base_test$time_int_end)
}



tmp <- seq(ISOdatetime(min(Base_test$year_start, Base_test$year_end),min(Base_test$month_start, Base_test$month_end),
                       min(Base_test$day_start, Base_test$day_end),min(Base_test$hour_start, Base_test$hour_end),0,0),
           ISOdatetime(max(Base_test$year_start, Base_test$year_end),max(Base_test$month_start, Base_test$month_end),
                       max(Base_test$day_start, Base_test$day_end),max(Base_test$hour_start, Base_test$hour_end),55,0), by=(60*5))

table_pu <- table_do  <- table_net_flow <- as.matrix(matrix(0, nrow = length(tmp), ncol = nlevels(Base_test$Start.station)))
colnames(table_pu) <- colnames(table_do) <- colnames(table_net_flow) <- c(levels(Base_test$Start.station))
rownames(table_pu) <- rownames(table_do) <- rownames(table_net_flow) <- as.character(tmp)

table_pu <- as.data.frame(table_pu)
table_do <- as.data.frame(table_do)
table_net_flow <- as.data.frame(table_net_flow)

library(plyr)
### Pick up/Start
table_count_start <- count(Base_test, vars=c("Start.station","year_start", "month_start", "day_start","hour_start","time_int_start"))

for(i in 1:nrow(table_count_start))
{
  table_pu[as.character(ISOdatetime(table_count_start$year_start[i],table_count_start$month_start[i],table_count_start$day_start[i],
                                    table_count_start$hour_start[i],table_count_start$time_int_start[i],0))
           ,as.character(table_count_start$Start.station[i])] <- table_count_start$freq[i]
}

table_pu[is.na(table_pu)] <- 0


### drop off/End
table_count_end <- count(Base_test, vars=c("End.station","year_end", "month_end", "day_end","hour_end","time_int_end"))

for(i in 1:nrow(table_count_end))
{
  table_do[as.character(ISOdatetime(table_count_end$year_end[i],table_count_end$month_end[i],table_count_end$day_end[i],table_count_end$hour_end[i],
                                    table_count_end$time_int_end[i],0))
           ,as.character(table_count_end$End.station[i])] <- table_count_end$freq[i]
}

table_do[is.na(table_do)] <- 0



for(i in 1:nrow(table_pu))
  for(j in 1:ncol(table_pu))
    table_net_flow[i,j] = table_do[i,j] - table_pu[i,j]

write.csv(table_net_flow, "net_flow_8_2018.csv")



################################################## Bivariate analysis ####################################################
library(ggplot2)
library(grid)
library(GoodmanKruskal)

setwd("C:/Users/sraoul/Documents/Hackathon/obs_netflow_1h")
df <- read.csv("obs_netflow.csv", sep=",")
df$X159 <- as.factor(df$X159)



fill <- "gold1"
line <- "goldenrod2"
p10 <- ggplot(df, aes(x = X159, y = temperature)) +
  geom_boxplot(fill = fill, colour = line) +
  scale_y_continuous(name = "Temperature",
                     breaks = seq(-15, 40, 5),
                     limits=c(-15, 40)) +
  scale_x_discrete(name = "Net Demand Station 159") +
  ggtitle("Boxplot of temperature per net demand")
p10




GKmatrix_dataset <- GKtauDataframe(df[,c("X159", "wind_direction_cat", "weather_fair.cloudy", "weather_fog.haze",
                                         "weather_thunderstorm", "weather_rain", "weather_snow", "weather_other")], 
                                   dgts = 2)
plot(GKmatrix_dataset)

