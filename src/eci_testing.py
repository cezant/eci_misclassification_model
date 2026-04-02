#!/usr/bin/env python
# coding: utf-8

# ## Objective
# 
# How much would the Employment Cost Index (ECI) change if a business or occupation were misclassified into the wrong NAICS industry or SOC occupation?

# ![image.png](attachment:e39af56f-5d04-467c-a131-77a19e060e86.png)

# In[1]:


import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt


# In[2]:


API_KEY = "5cb8d1aaf19a44f2b6c6d2436e78cee3"


# In[3]:


series_ids = [
    "CIU2010000000000A",  # total compensation
    "CIU2020000000000A"   # wages & salaries
]

url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

payload = {
    "seriesid": series_ids,
    "startyear": "2015",
    "endyear": "2024",
    "registrationkey": API_KEY
}

response = requests.post(url, json=payload)
data = response.json()


# In[4]:


records = []

for s in data["Results"]["series"]:
    sid = s["seriesID"]

    for obs in s["data"]:
        records.append({
            "series_id": sid,
            "year": int(obs["year"]),
            "period": obs["period"],
            "value": float(obs["value"])
        })

eci_df = pd.DataFrame(records)

eci_df.head()


# In[5]:


eci_df = eci_df[eci_df["period"] == "Q04"]  #Official Wage Index


# ## Retrieving Real occupational data (OEWS)  #(https://www.bls.gov/oes/special-requests/oesm23nat.zip)  This will help build a model of wages or wage index

# In[6]:


oews = pd.read_excel(r"E:\BLS_Project\national_M2023_dl.xlsx")  #loading the OEWS Data

oews.head()


# In[7]:


oews = oews[["OCC_CODE", "OCC_TITLE", "TOT_EMP", "A_MEAN"]]


# In[8]:


oews = oews.dropna(subset=["TOT_EMP", "A_MEAN"])


# In[9]:


oews["TOT_EMP"] = pd.to_numeric(oews["TOT_EMP"], errors="coerce")
oews["A_MEAN"] = pd.to_numeric(oews["A_MEAN"], errors="coerce")


# In[10]:


oews = oews.dropna(subset=["TOT_EMP", "A_MEAN"])


# In[11]:


#renaming columns
oews.rename(columns={
    "OCC_CODE": "SOC",
    "TOT_EMP": "employment",
    "A_MEAN": "avg_wage"
}, inplace=True)


# In[12]:


oews.head()


# In[13]:


#missing values??
print(oews.isna().sum())


# ## Now I will remove 00-0000  → "All Occupations", since everything is already averaged, otherwise it will double count the entire economy

# In[14]:


oews = oews[oews["SOC"] != "00-0000"]


# In[15]:


# This will calculate weighted wages 

oews["weighted_wage"] = oews["employment"] * oews["avg_wage"]


# In[40]:


# Building a True Index or Weighted Wage Index

#total money paid to everyone/ total number of workers
true_index = oews["weighted_wage"].sum() / oews["employment"].sum()

print("True Wage Index:", true_index)


# ## Simulating Misclassification

# In[42]:


def misclassify_soc(data, rate=0.05):  #where data=my oews dataset, rate=5%

    df = data.copy()  #creates a copy

    n = int(len(df) * rate) #-----> calculation of how many rows to mess up since 800 occupations exist x .05 =40rows so n=40

    idx = np.random.choice(df.index, n, replace=False)  #randomly selects n rows (or jobs)

    random_wages = np.random.choice(df["avg_wage"], n)  #This one then randomly grabs the wages from other jobs

    df.loc[idx, "avg_wage"] = random_wages  #for the selected rows, it replaces their wages with the wrong ones

    return df   #<----That will then yield a new dataset with wrong rate


# In[43]:


simulated = misclassify_soc(oews, rate=0.05)  #In this case “5% of jobs are  wrong”


# ## Now Recalculating the Index

# In[44]:


simulated["weighted_wage"] = simulated["employment"] * simulated["avg_wage"]

distorted_index = simulated["weighted_wage"].sum() / simulated["employment"].sum()

print("Distorted Index:", distorted_index)


# ## Measuring the IMPACT

# In[45]:


impact = distorted_index - true_index

print("Impact on Index:", impact)


# ### Thus in this simulation above, if 5% of jobs are misclassified incorrectly the average wage estimate increased (or decreased) by about 952.66. Thus the average wage 65,465 and after the mistake average wage could be 64,512.34 or 66,418.40 because of the impact of the =$952.66.

# ## Converting Impact to Percentage

# In[46]:


percent_impact = (impact / true_index) * 100

print("Percent Impact:", percent_impact, "%")  
#In other words 171/65465 = 0.01455 or 1.45% or a 5% misclassification rate causes the wage index to be biased by +1.45%

#If 5% of workers are misclassified, the published wage index could be off by ~1.45%


# ## Multiple Scenarios

# In[49]:


#Simulation Loop using various error rates

rates = [0.01, 0.05, 0.10, 0.20]  #error rates, 1%, 5%, 10% or 20%

results = []

for r in rates:

    sim = misclassify_soc(oews, r)

    sim["weighted_wage"] = sim["employment"] * sim["avg_wage"]

    new_index = sim["weighted_wage"].sum() / sim["employment"].sum()

    impact = new_index - true_index

    percent_impact = (impact / true_index) * 100

    results.append([r, new_index, impact, percent_impact])


# In[50]:


results_df = pd.DataFrame(
    results,
    columns=["Misclassification Rate", "New Index", "Dollar Impact", "Percent Impact"]
)

print(results_df)


# ### ECI is sensitive to classification errors.  Naturally as errors increase--> distortion increases

# ## Visual interpretation of errors

# In[77]:


import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,6))
plt.plot(
    results_df["Misclassification Rate"],
    results_df["Percent Impact"],
    marker='o'
)

plt.xlabel("Misclassification Rate")
plt.ylabel("Percent Impact on Index")

plt.title("Sensitivity of Wage Index to SOC Misclassification")
fig.savefig(r"E:\BLS_Project\output\sensitivity_soc_miscl.png",
            dpi=300,
            bbox_inches="tight")

plt.show()


# #### X Axis is the % error, The Y Axis is the impact % to the index

# In[52]:


eci_clean = eci_df[eci_df["period"] == "Q04"].copy()

eci_clean.rename(columns={"value": "growth"}, inplace=True)


# In[53]:


eci_clean = eci_clean.sort_values("year")

print(eci_clean[["year", "growth"]])

# This eci_clean will yield 2 rows per year.  This is because  i used 2 different eci series 1) wages & salaries 2)total compensation, 
#since I have both i will average them to create a stable benchmark.


# In[54]:


#this will average them out by year
eci_avg = eci_clean.groupby("year")["growth"].mean().reset_index()

print(eci_avg)


# In[55]:


eci_growth_avg = eci_avg["growth"].mean()

print("Final ECI Growth:", eci_growth_avg)


# ## Comparing both eci_growth_avg to model

# In[63]:


print("Model Impact:", percent_impact) #model
print("ECI Growth:", eci_growth_avg) #eci growth ave.


# In[57]:


eci_growth_avg = eci_avg["growth"].mean()

print("Final ECI Growth:", eci_growth_avg)


# #### Summary:
# 
# ## A 5% misclassification rate produces approximately a 1.45% bias in the wage index, representing roughly 43.83% of observed annual ECI wage growth.

# In[66]:


impact = distorted_index - true_index
percent_impact = (impact / true_index) * 100



# In[60]:


eci_growth_avg = eci_avg["growth"].mean()


# In[61]:


share_of_growth = percent_impact / eci_growth_avg

print("Model Percent Impact:", percent_impact)
print("Average ECI Growth:", eci_growth_avg)
print("Share of ECI explained by misclassification:", share_of_growth)


# In[62]:


share_percent = share_of_growth * 100

print("Percent of ECI growth explained:", share_percent, "%")


# # How certain are we of the effect?
# ### The simulation now will run 1000 times

# In[67]:


bias_shares = []

for i in range(1000):

    sim = misclassify_soc(oews, rate=0.05)

    sim["weighted_wage"] = sim["employment"] * sim["avg_wage"]

    new_index = sim["weighted_wage"].sum() / sim["employment"].sum()

    impact = new_index - true_index

    percent_impact = (impact / true_index) * 100

    share = percent_impact / eci_growth_avg

    bias_shares.append(share)


# In[68]:


#converting to percentage

bias_shares = np.array(bias_shares) * 100


# ## Summary of results below

# In[69]:


print("Average Bias Share:", np.mean(bias_shares))
print("Min Bias Share:", np.min(bias_shares))
print("Max Bias Share:", np.max(bias_shares))
print("Std Dev:", np.std(bias_shares))


# In[70]:


# Confidence Interval:
lower = np.percentile(bias_shares, 5)
upper = np.percentile(bias_shares, 95)

print("90% Confidence Interval:", lower, "to", upper)


# # BIG PROBLEM WITH MY MODEL ABOVE:
# 
# ## On average, the misclassification explains about 18% of observed ECI wage growth.  However, there is a problem with the randomness of the model above.  Because of the randomness ANY JOB can be misclasified as any other job.  Which explains why the Min Bias share can be -105.37 and Max Bias can be up to 348.  The model moving forward will now use a more structured misclassificcation.

# In[72]:


# First I will create SOC groups:

oews["SOC_group"] = oews["SOC"].str[:2]  #grouping similar occupations using the first 2 digits of SOCs.


# In[73]:


def misclassify_realistic(data, rate=0.05):  

    df = data.copy()

    n = int(len(df) * rate)

    idx = np.random.choice(df.index, n, replace=False)

    for i in idx:

        group = df.loc[i, "SOC_group"]  #

        # Only pick similar occupations
        group_df = df[df["SOC_group"] == group]

        if len(group_df) > 1:
            new_wage = np.random.choice(group_df["avg_wage"])
            df.loc[i, "avg_wage"] = new_wage

    return df


# ### previous function we def "random misclassification" in the def above we are using a more realistic model "misclassify_realistic".

# In[74]:


#Re-runing of simulation model with the "misclassify_realistic"
bias_shares = []

for i in range(1000):

    sim = misclassify_realistic(oews, rate=0.05)

    sim["weighted_wage"] = sim["employment"] * sim["avg_wage"]

    new_index = sim["weighted_wage"].sum() / sim["employment"].sum()

    impact = new_index - true_index

    percent_impact = (impact / true_index) * 100

    share = percent_impact / eci_growth_avg

    bias_shares.append(share * 100)


# In[75]:


print("Average:", np.mean(bias_shares))
print("Min:", np.min(bias_shares))
print("Max:", np.max(bias_shares))
print("Std:", np.std(bias_shares))

print("90% CI:",
      np.percentile(bias_shares, 5),
      "to",
      np.percentile(bias_shares, 95))


# # Now with the newer model on average, misclassification explains about 14% of observed ECI wage growth.  However the distribution of outcoes remains wide, with a 90% confidence interval ranging from -21% to +74%, indicating that the direction and magnitude of the bias depends heavily on the specific pattern of misclassification.

# In[ ]:




