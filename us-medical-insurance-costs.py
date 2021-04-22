import csv
from matplotlib import pyplot as plt
import numpy as np

def load_dataset(filename):
  with open(filename) as csvfile:
    csv_reader = csv.DictReader(csvfile)
    data_out = {"age":[], "sex":[], "bmi":[], "children":[], "smoker":[], "region":[], "charges":[]}
    for row in csv_reader:
      data_out["age"].append(float(row["age"]))
      data_out["sex"].append(row["sex"])
      data_out["bmi"].append(float(row["bmi"]))
      data_out["children"].append(int(row["children"]))
      data_out["smoker"].append(row["smoker"])
      data_out["region"].append(row["region"])
      data_out["charges"].append(float(row["charges"]))
  return data_out


def select_data(insurance_data, keys_of_interest, selection):
  data_out = {}
  for key in keys_of_interest:
    data_out.update({key:[]})
  for key in list(insurance_data.keys()):
    selection = selection.replace(key, "insurance_data['{}'][i]".format(key))
  for i in range(len(insurance_data[keys_of_interest[0]])):
    if eval(selection):
      for key in keys_of_interest:
        data_out[key].append(insurance_data[key][i])
  return data_out


def find_mean_and_sd(data_list):
  mean = 0.0;
  meansqrs = 0.0
  for num in data_list:
    mean += float(num)
    meansqrs += float(num)**2
  mean = mean/len(data_list)
  meansqrs = meansqrs/len(data_list)
  sd = (meansqrs - mean**2) ** 0.5
  return round(mean, 2), round(sd, 2)


def minima_only(insurance_data, var_name):
  minima_data = {}
  for index in range(len(insurance_data[var_name])):
    key = insurance_data[var_name][index]
    cost = insurance_data["charges"][index]
    if not (key in minima_data.keys()):
      minima_data.update({float(key):float(cost)})
    else:
      if cost < minima_data[key]:
        minima_data[key] = float(cost)
  return minima_data


def get_chi_squared(osbserved, expected):
  chisqr = sum([((o - e)**2) / e for o, e in zip(observed, expected)])
  return chisqr


# Main analysis code:
insurance_data = load_dataset("insurance.csv")
average_age, sd_age = find_mean_and_sd(insurance_data["age"])
print("The average age of patients in the dataset is {age} with a standard deviation of {sd}".format(age=average_age, sd=sd_age))

print("\nLet's see how smoking affects the cost of insurance:")
smoker_data = select_data(insurance_data, list(insurance_data.keys()), "smoker=='yes'")
smoker_cost, smoker_cost_sd = find_mean_and_sd(smoker_data["charges"])
print("The average insurance cost for smokers in the dataset is ${avg} with a standard deviation of ${sd}".format(avg=smoker_cost, sd=smoker_cost_sd))

nonsmoker_data = select_data(insurance_data, list(insurance_data.keys()), "smoker=='no'")
nonsmoker_cost, nonsmoker_cost_sd = find_mean_and_sd(nonsmoker_data["charges"])
print("The average insurance cost for non-smokers in the dataset is ${avg} with a standard deviation of ${sd}".format(avg=nonsmoker_cost, sd=nonsmoker_cost_sd))

print("On average, being a smoker increases the cost of insurance by ${}".format(round(smoker_cost - nonsmoker_cost, 2)))

print("\nLet's see how gender affects the cost of insurance:")
male_data = select_data(insurance_data, list(insurance_data.keys()), "sex=='male' and smoker=='no'")
male_cost, male_cost_sd = find_mean_and_sd(male_data["charges"])
print("The average insurance cost for male non-smokers in the dataset is ${avg} with a standard deviation of ${sd}".format(avg=male_cost, sd=male_cost_sd))

female_data = select_data(insurance_data, list(insurance_data.keys()), "sex=='female' and smoker=='no'")
female_cost, female_cost_sd = find_mean_and_sd(female_data["charges"])
print("The average insurance cost for female non-smokers in the dataset is ${avg} with a standard deviation of ${sd}".format(avg=female_cost, sd=female_cost_sd))
print("On average, among non-smokers, being female increases the cost of insurance by ${}".format(round(female_cost - male_cost, 2)))

print("\nLet's see how BMI affects the cost of insurance:")
goodBMI_data = select_data(insurance_data, list(insurance_data.keys()), "bmi>=18.5 and bmi<=24.9 and smoker=='no'")
goodBMI_cost, goodBMI_cost_sd = find_mean_and_sd(goodBMI_data["charges"])
print("The average insurance cost for patients with a BMI in the healthy range (18.5-24.9) is ${avg} with a standard deviation of ${sd}".format(avg=goodBMI_cost, sd=goodBMI_cost_sd))

badBMI_data = select_data(insurance_data, list(insurance_data.keys()), "bmi<18.5 or bmi>24.9 and smoker=='no'")
badBMI_cost, badBMI_cost_sd = find_mean_and_sd(badBMI_data["charges"])
print("The average insurance cost for patients with a BMI outside the healthy range (18.5-24.9) is ${avg} with a standard deviation of ${sd}".format(avg=badBMI_cost, sd=badBMI_cost_sd))
print("On average, among non-smokers, having a BMI outside the healthy range increases the cost of insurance by ${}".format(round(badBMI_cost - goodBMI_cost, 2)))
print("\n")

print("Let's look at a plot of charges versus age:")
plt.scatter(insurance_data["age"], insurance_data["charges"])
plt.xlabel("age")
plt.ylabel("charges")
#plt.show()
print("There seems to be a minimum insurance cost that varies smoothly with age. Let's fit a line to those minimum points to see how the base insurance cost is calculated.\n")

min_cost_by_age = minima_only(insurance_data, "age")
xarray = list(min_cost_by_age.keys())
yarray = list(min_cost_by_age.values())
plt.scatter(xarray, yarray)
plt.xlabel("age")
plt.ylabel("charges")
a, b, c = np.polyfit(xarray, yarray, 2)
xline = sorted(xarray)
yline = [a*x**2 + b*x + c for x in xline]
plt.plot(xline, yline, color="red")
plt.show()
print("The base insurance cost is calculated from the patient age as cost = {a}*age**2 + {b}*age + {c}\n".format(a=round(a,2), b=round(b,2), c=round(c,2)))


# Create a new dataset, subtracting out the minimum insurance cost by age that we just discovered.
ageless_data = select_data(insurance_data, list(insurance_data.keys()), "True")
for i in range(len(ageless_data["charges"])):
  x = ageless_data["age"][i]
  y = ageless_data["charges"][i] - (a*x**2 + b*x + c)
  ageless_data["charges"][i] = y

plt.scatter(ageless_data["children"], ageless_data["charges"])
plt.xlabel("children")
plt.ylabel("charges")
print("After removing the dependence on age, we can now clearly see that the lowest insurance charges increase with the number of children.\n")
min_cost_by_children = minima_only(ageless_data, "children")
xarray = list(min_cost_by_children.keys())
yarray = list(min_cost_by_children.values())
plt.scatter(xarray, yarray)
plt.xlabel("children")
plt.ylabel("charges")
d, e = np.polyfit(xarray, yarray, 1)
xline_children = sorted(xarray)
yline_children = [d*x + e for x in xline_children]
plt.plot(xline_children, yline_children, color="red")
plt.show()
print("The additional cost from children is {d}*(# of children) + {e}\n".format(d=round(d,2), e=round(e,2)))


# Create a new dataset, subtracting out the minimum insurance cost by number of children.
ageless_childless_data = select_data(ageless_data, list(ageless_data.keys()), "True")
for i in range(len(ageless_childless_data["charges"])):
  x = ageless_childless_data["children"][i]
  y = ageless_childless_data["charges"][i] - (d*x + e)
  ageless_childless_data["charges"][i] = y

plt.scatter(ageless_childless_data["bmi"], ageless_childless_data["charges"])
plt.xlabel("bmi")
plt.ylabel("charges")

print("After removing the dependence on age and number of children, we can now clearly see three distinct regions of points in the graph of charges versus BMI. The bottom line, which shows no dependence on BMI, corresponds to non-smokers. The two regions above correspond to smokers, where there appears to be a constant slope and a discontinuous jump at a value of 30.\n")


ageless_childless_smoker_thin_data = select_data(ageless_childless_data, list(ageless_childless_data.keys()), "smoker=='yes' and bmi<=30 and charges<18000") # cut out high charges to ignore outliers which are probability based on unknown pre-existing conditions.
xarray = ageless_childless_smoker_thin_data["bmi"]
yarray = ageless_childless_smoker_thin_data["charges"]
f, g = np.polyfit(xarray, yarray, 1)
xline_thin_smoker = sorted(xarray)
yline_thin_smoker = [f*x + g for x in xline_thin_smoker]
plt.plot(xline_thin_smoker, yline_thin_smoker, color="red")

ageless_childless_smoker_fat_data = select_data(ageless_childless_data, list(ageless_childless_data.keys()), "smoker=='yes' and bmi>30 and charges<43000")
xarray = ageless_childless_smoker_fat_data["bmi"]
yarray = ageless_childless_smoker_fat_data["charges"]
h, j = np.polyfit(xarray, yarray, 1)
xline_fat_smoker = sorted(xarray)
yline_fat_smoker = [h*x + j for x in xline_fat_smoker]
plt.plot(xline_fat_smoker, yline_fat_smoker, color="red")
plt.show()

print("The extra cost a smoker incurs is calculated based on their BMI as follows. If the BMI<=30, then the cost = {f}*BMI + {g}. If BMI>30, then cost = {h}*BMI + {j}\n".format(f=round(f,2), g=round(g,2), h=round(h,2), j=round(j,2)))


# Function to predict cost of insurance:
def predict_charges(age, bmi, children, smoker):

  # age factor
  charges = 2.92*age**2 + 35.15*age - 501.62

  # children factor
  charges += 591.27*children - 169.89

  # smoker/bmi factor
  if smoker=='yes':
    if bmi<=30:
      charges += 465.15*bmi + 2705.79
    else:
      charges += 451.08*bmi + 18528.39

  return charges

# Calculate the chi-squared value:
observed = insurance_data["charges"]
variables = zip(insurance_data["age"], insurance_data["bmi"], insurance_data["children"], insurance_data["smoker"])
expected = [predict_charges(age, bmi, children, smoker) for age, bmi, children, smoker in variables]
chi_squared = get_chi_squared(observed, expected)
print("The chi-squared value is {}".format(chi_squared))
num_points = len(insurance_data["charges"])
num_parameters = 9
dof = num_points - num_parameters 
chi_squared_dof = chi_squared/dof
print("The chi-squared value per degree-of-freedom is {}".format(chi_squared_dof))
