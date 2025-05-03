#!/usr/bin/env Rscript
# Stage 6 – Bayesian Credit Risk Modeling (advanced)
# ---------------------------------------------------
# Fits a Bayesian logistic regression (default vs non-default) using
# rstanarm, leveraging PD/LGD & borrower characteristics.
# Generates posterior PD estimates and calibration plots.

suppressPackageStartupMessages({
  library(tidyverse)
  library(rstanarm)   # for bayesian glm
})

# Helpers -----------------------------------------------------------------
project_root <- here::here()
credit_path <- file.path(project_root, "credit_risk_loans.csv")
output_dir <- file.path(project_root, "output")
if (!dir.exists(output_dir)) dir.create(output_dir)

# Data --------------------------------------------------------------------
credit <- read_csv(credit_path, show_col_types = FALSE) %>%
  mutate(DefaultFlag = as.integer(DefaultFlag))

# Simple features (rating ordered as numeric)
rating_levels <- c("AAA", "AA", "A", "BBB", "BB", "B")
credit <- credit %>%
  mutate(RatingOrd = as.integer(factor(Rating, levels = rating_levels, ordered = TRUE)))

# Model -------------------------------------------------------------------
set.seed(123)
fit <- stan_glm(
  DefaultFlag ~ RatingOrd + LGD + PD + Sector,
  data = credit,
  family = binomial(link = "logit"),
  chains = 4, iter = 2000, refresh = 0
)

print(summary(fit), digits = 2)

# Posterior PD -------------------------------------------------------------
credit$PostPD <- posterior_epred(fit, newdata = credit) %>%
  apply(2, mean)

write_csv(credit %>% select(LoanID, PD, PostPD, DefaultFlag),
          file.path(output_dir, "cr_bayesian_pd.csv"))

# Calibration plot ---------------------------------------------------------
ggplot(credit, aes(x = PD, y = PostPD)) +
  geom_point(alpha = 0.4, colour = "#3E6C72") +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", colour = "#C46A2B") +
  labs(title = "Posterior PD vs Prior PD", x = "Prior PD", y = "Posterior PD") +
  theme_minimal(base_family = "Helvetica") +
  theme(panel.background = element_rect(fill = "#F8F9FA"),
        plot.background = element_rect(fill = "#F8F9FA"),
        text = element_text(colour = "#1A2A4B"))

ggsave(file.path(output_dir, "cr_posterior_pd_calibration.png"), dpi = 300, width = 6, height = 4) 