library(tidyverse)
library(extrafont)

font_import()
loadfonts()

equilibrium <- read_csv("3_bidders_13_valuations.csv")

first_equilibrium <- filter(equilibrium, Equilibria == 1)

temp <- select(first_equilibrium, -Equilibria, -Player)
temp <- rownames_to_column(temp)
temp <- gather(temp, var, value, -rowname)
temp <- spread(temp, rowname, value)
temp <- mutate(temp, valuation = as.numeric(str_sub(var, 11, nchar(var))))
temp <- mutate(temp, cont_bid = valuation * 2.0 / 3.0)


temp <- rename(temp, bidder_1 = 2)
temp <- rename(temp, bidder_2 = 3)
temp <- rename(temp, bidder_3 = 4)

alpha_value <- 0.5
size_value <- 1.8
font_size <- 15

ggplot(data = temp) + 
  theme_bw() +
  xlab("Valuation") + 
  ylab("Bid") +
  geom_step(mapping = aes(x = valuation, y = bidder_1, group = 1), color='red', alpha = alpha_value, size = size_value) +
  geom_step(mapping = aes(x = valuation, y = bidder_2, group = 2), color='blue', alpha = alpha_value, size = size_value) +
  geom_step(mapping = aes(x = valuation, y = bidder_3, group = 3), color='darkgreen',alpha = alpha_value, size = size_value) +
  geom_line(mapping = aes(x = valuation, y = cont_bid, group = 4), linetype = "dashed") +
  expand_limits(x = 0, y = 0) +
  scale_x_continuous(expand = c(0, 0)) + 
  scale_y_continuous(expand = c(0, 0)) +
  theme(text=element_text(size=font_size, family='Times New Roman'),
        panel.border = element_blank(),
        panel.grid.major.x= element_blank(),
        panel.grid.minor.x = element_blank(),
        axis.line = element_line(size=.3, color="black"))


  
