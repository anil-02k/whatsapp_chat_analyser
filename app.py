import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8-sig")  # Handle BOM encoding
        df = preprocessor.preprocess(data)
        
        if df.empty:
            st.error("Error processing data: No valid messages found")
            st.stop()

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

        if st.sidebar.button("Show Analysis"):
            # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

            # Monthly Timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            if not timeline.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(timeline['time'], timeline['count'], color='green')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("No data available for monthly timeline")

            # Daily Timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            if not daily_timeline.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(daily_timeline['only_date'], daily_timeline['count'], color='black')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("No data available for daily timeline")

            # Activity Map
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                if not busy_day.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.warning("No data available for weekly activity")

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                if not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.warning("No data available for monthly activity")

            # Weekly Activity Heatmap
            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if not user_heatmap.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.heatmap(user_heatmap, ax=ax)
                st.pyplot(fig)
            else:
                st.warning("No data available for activity heatmap")

            # Busiest Users Analysis
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                if not x.empty and not new_df.empty:
                    fig, ax = plt.subplots()
                    col1, col2 = st.columns(2)
                    with col1:
                        ax.bar(x.index, x.values, color='red')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)
                else:
                    st.warning("No user data available")

            # WordCloud
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            if df_wc is not None:
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.warning("No data available for word cloud")

            # Most Common Words
            st.title('Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            if not most_common_df.empty:
                fig, ax = plt.subplots()
                ax.barh(most_common_df['Word'], most_common_df['Count'])
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("No common words found")

            # Emoji Analysis
            st.title("Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df['Count'].head(), 
                          labels=emoji_df['Emoji'].head(),
                          autopct="%0.2f")
                    st.pyplot(fig)
            else:
                st.warning("No emojis found in messages")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.stop()