import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Menyiapkan DataFrame jumlah penyewa sepeda perbulan
def create_sum_monthly_user_df(df):
    sum_monthly_user_df =df.resample(rule='M', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    sum_monthly_user_df.index = sum_monthly_user_df.index.strftime('%B')
    sum_monthly_user_df = sum_monthly_user_df.reset_index()
    sum_monthly_user_df.rename(columns={
        "instant": "total day in a month",
        "cnt": "total user in a month"
    }, inplace=True)
    
    return sum_monthly_user_df

# Menyiapkan DataFrame jumlah penyewa sepeda per musim
def create_sum_user_byseason_df(df):
    sum_user_byseason_df = df.groupby("name of season").cnt.sum().sort_values(ascending=False).reset_index()
    
    sum_user_byseason_df.rename(columns={
    "cnt": "total user by season"
    }, inplace=True)
    
    return sum_user_byseason_df

# Menyiapkan DataFrame RFM Analysis
def create_rfm_df(df):
    df['month'] = df['dteday'].dt.month
    df['season'] = df['name of season']
    df['user'] =df['cnt']
    
    current_date = df['dteday'].max()
    df['recency'] = (current_date - df['dteday']).dt.days
    df['frequency'] = df.groupby('name of season')['dteday'].transform('count')
    df['monetary'] = df['cnt']
    
    rfm_result = df.groupby('name of season').agg({
    'recency': 'min',
    'frequency': 'sum',
    'monetary': 'sum'
    }).reset_index()
    
    return df, rfm_result

# Memuat data_new csv sebagai DataFrame
data_new_df = pd.read_csv("data_new.csv")

# Mengurutkan DataFrame berdasarkan dteday dan memastikan kolomnya bertipe datetime
datetime_columns = ["dteday"]
data_new_df.sort_values(by="dteday", inplace=True)
data_new_df.reset_index(inplace=True)
 
for column in datetime_columns:
    data_new_df[column] = pd.to_datetime(data_new_df[column])

# Membuat komponen filter
min_date = data_new_df["dteday"].min()
max_date = data_new_df["dteday"].max()

with st.sidebar:

    st.text('Calendar')
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memfilter data berdasarkan main_df
main_df = data_new_df[(data_new_df["dteday"] >= str(start_date)) & 
                (data_new_df["dteday"] <= str(end_date))]

sum_monthly_user_df = create_sum_monthly_user_df(main_df)
sum_user_byseason_df = create_sum_user_byseason_df(main_df)
df = create_rfm_df(main_df)
rfm_result = create_rfm_df(main_df)


st.header('Bike Sharing Dashboard')   # Membuat judul dashboard

# Membuat metrik total monthly users
st.subheader('Total Monthly Users')
 
col1 = st.columns(1)

total_users = sum_monthly_user_df['total user in a month'].sum()
st.metric("Total Users", value=total_users)

# Membuat line plot total monthly users
plt.figure(figsize=(10, 6))
plt.plot(sum_monthly_user_df['dteday'], sum_monthly_user_df['total user in a month'], marker='o', linewidth=3, color="#414F69")

plt.xlabel('Month')
plt.ylabel('Total Users')
plt.title('Number of Users per Month in 2011')
plt.xticks(rotation=45)

fig = plt.gcf()
st.pyplot(fig)

# Membuat metrik user by season
st.subheader('Total Users By Season')
 
col1 = st.columns(1)

total_users = sum_user_byseason_df['total user by season'].sum()
st.metric("Total Users", value=total_users)

# Membuat dan menampilkan bar plot total user by season
plt.figure(figsize=(10, 5))
colors_ = ["#414F69", "#BABACB", "#BABACB", "#BABACB"]
 
sns.barplot(
    y="total user by season", 
    x="name of season",
    data=sum_user_byseason_df.sort_values(by="total user by season", ascending=False),
    palette=colors_
)
plt.title("Number of users by season", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

fig = plt.gcf()
st.pyplot(fig)

def metrik(metric_name, metric_value):    # Membuat metrik RFM
    st.metric(label=metric_name, value=metric_value)

df, rfm_result = create_rfm_df(data_new_df)

st.title("RFM Analysis Metrics by Season") # Membuat judul metrik

for index, row in rfm_result.iterrows():
    Name_of_season = row['name of season']

    # Membuat dan menampilkan bar plot RFM Analysis
    fig, ax = plt.subplots()
    ax.bar(['Recency', 'Frequency', 'Monetary'], [row['recency'], row['frequency'], row['monetary']])
    ax.set_ylabel('Value')
    ax.set_title(f'Metrics for {Name_of_season}')
   
    st.pyplot(fig)
    
    # Menampilkan metrik RFM Analysis
    metrik(f"Recency ({Name_of_season})", row['recency'])
    metrik(f"Frequency ({Name_of_season})", row['frequency'])
    metrik(f"Monetary ({Name_of_season})", row['monetary'])







