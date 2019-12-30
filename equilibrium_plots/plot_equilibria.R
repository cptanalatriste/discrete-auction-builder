library(tidyverse)

equilibrium <- read_csv("3_bidders_no_ties_7_valuations.csv")

first_equilibrium <- filter(equilibrium, Equilibria == 1)

temp <- select(first_equilibrium, -Equilibria, -Player)
temp <- rownames_to_column(temp)
temp <- gather(temp, var, value, -rowname)
temp <- spread(temp, rowname, value)
temp <- mutate(temp, valuation = as.numeric(str_sub(var, nchar(var), nchar(var))))
temp <- mutate(temp, cont_bid = valuation * 2.0 / 3.0)


temp <- rename(temp, bidder_1 = 2)
temp <- rename(temp, bidder_2 = 3)
temp <- rename(temp, bidder_3 = 4)

ggplot(data = temp) + 
  xlab("Valuation") + 
  ylab("Bid") +
  geom_line(mapping = aes(x = valuation, y = bidder_1, group = 1), color="red", alpha = 0.3) +
  geom_line(mapping = aes(x = valuation, y = bidder_2, group = 2), color='blue', alpha = 0.3) +
  geom_line(mapping = aes(x = valuation, y = bidder_3, group = 3), color='green',alpha = 0.3) +
  geom_line(mapping = aes(x = valuation, y = cont_bid, group = 4), linetype = "dashed") 
  
