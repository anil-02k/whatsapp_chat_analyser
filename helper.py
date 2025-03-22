from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import re
from typing import Tuple, List, Optional
import numpy as np

extract = URLExtract()

def fetch_stats(selected_user: str, df: pd.DataFrame) -> Tuple[int, int, int, int]:
    """
    Fetch basic statistics about messages for a selected user.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        Tuple[int, int, int, int]: (num_messages, num_words, num_media, num_links)
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    stats = {
        'num_messages': 0,
        'num_words': 0,
        'num_media': 0,
        'num_links': 0
    }
    
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        stats['num_messages'] = df.shape[0]
        
        # Word count (excluding media messages)
        words = []
        for message in df[df['message'] != '<Media omitted>']['message']:
            words.extend(message.split())
        stats['num_words'] = len(words)
        
        # Media messages
        stats['num_media'] = df[df['message'] == '<Media omitted>'].shape[0]
        
        # URL extraction
        links = []
        for message in df['message']:
            links.extend(extract.find_urls(message))
        stats['num_links'] = len(links)

    except Exception as e:
        raise ValueError(f"Error in fetch_stats: {str(e)}")
    
    return (
        stats['num_messages'],
        stats['num_words'],
        stats['num_media'],
        stats['num_links']
    )

def most_busy_users(df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Find the most active users in the chat.
    
    Args:
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        Tuple[pd.Series, pd.DataFrame]: (user_counts, percentage_df)
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        user_counts = df[df['user'] != 'system']['user'].value_counts().head(10)
        if user_counts.empty:
            raise ValueError("No valid users found in the chat")
            
        percent_df = pd.DataFrame({
            'User': user_counts.index,
            'Message Count': user_counts.values,
            'Percentage': (user_counts / user_counts.sum() * 100).round(2)
        })
        return user_counts, percent_df
    except Exception as e:
        raise ValueError(f"Error in most_busy_users: {str(e)}")

def create_wordcloud(selected_user: str, df: pd.DataFrame) -> Optional[WordCloud]:
    """
    Create a word cloud from chat messages.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        Optional[WordCloud]: Generated word cloud or None if error occurs
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        # Load stop words
        try:
            with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        except FileNotFoundError:
            print("Warning: stop_hinglish.txt not found, using empty stop words set")
            stop_words = set()

        # Filter data
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")
        
        temp = df[(df['user'] != 'system') & 
                (df['message'] != '<Media omitted>')]
                
        if temp.empty:
            raise ValueError("No valid messages found for word cloud generation")

        # Generate wordcloud
        wc = WordCloud(
            width=800, 
            height=800,
            background_color='white',
            stopwords=stop_words,
            min_font_size=10,
            max_font_size=150,
            random_state=42
        )
        
        text = ' '.join(temp['message'].str.lower())
        if not text.strip():
            raise ValueError("No valid text found for word cloud")
            
        wc.generate(text)
        return wc

    except Exception as e:
        print(f"Error in create_wordcloud: {str(e)}")
        return None

def most_common_words(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Find most common words in chat messages.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with word counts
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        # Load stop words
        try:
            with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        except FileNotFoundError:
            print("Warning: stop_hinglish.txt not found, using empty stop words set")
            stop_words = set()

        # Filter data
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")
        
        temp = df[(df['message'] != '<Media omitted>') & 
                (df['user'] != 'system')]
                
        if temp.empty:
            raise ValueError("No valid messages found for word analysis")

        # Process messages
        words = []
        for message in temp['message']:
            for word in re.findall(r'\b[a-zA-Z]+\b', message.lower()):
                if word not in stop_words and len(word) > 2:
                    words.append(word)

        if not words:
            raise ValueError("No valid words found after processing")

        # Create DataFrame
        common_df = pd.DataFrame(Counter(words).most_common(20), 
                               columns=['Word', 'Count'])
        return common_df

    except Exception as e:
        raise ValueError(f"Error in most_common_words: {str(e)}")

def emoji_helper(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze emoji usage in chat messages.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with emoji counts
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        emojis = []
        for message in df['message']:
            emojis.extend([c for c in message if emoji.is_emoji(c)])

        if not emojis:
            return pd.DataFrame(columns=['Emoji', 'Count'])
            
        emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))),
                            columns=['Emoji', 'Count'])
        return emoji_df

    except Exception as e:
        raise ValueError(f"Error in emoji_helper: {str(e)}")

def monthly_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Create monthly message timeline.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.DataFrame: Monthly message counts
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        timeline = df.groupby(['year', 'month_num', 'month']).size().reset_index(name='count')
        timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
        return timeline
    except Exception as e:
        raise ValueError(f"Error in monthly_timeline: {str(e)}")

def daily_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Create daily message timeline.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.DataFrame: Daily message counts
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        return df.groupby('only_date').size().reset_index(name='count')
    except Exception as e:
        raise ValueError(f"Error in daily_timeline: {str(e)}")

def week_activity_map(selected_user: str, df: pd.DataFrame) -> pd.Series:
    """
    Create weekly activity map.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.Series: Message counts by day of week
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        return df['day_name'].value_counts().reindex([
            'Monday', 'Tuesday', 'Wednesday', 
            'Thursday', 'Friday', 'Saturday', 'Sunday'
        ], fill_value=0)
    except Exception as e:
        raise ValueError(f"Error in week_activity_map: {str(e)}")

def month_activity_map(selected_user: str, df: pd.DataFrame) -> pd.Series:
    """
    Create monthly activity map.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.Series: Message counts by month
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        return df['month'].value_counts().reindex([
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ], fill_value=0)
    except Exception as e:
        raise ValueError(f"Error in month_activity_map: {str(e)}")

def activity_heatmap(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Create activity heatmap by day and hour.
    
    Args:
        selected_user (str): User to analyze ('Overall' for all users)
        df (pd.DataFrame): Processed chat DataFrame
        
    Returns:
        pd.DataFrame: Activity heatmap matrix
        
    Raises:
        ValueError: If DataFrame is empty or invalid
    """
    if df.empty:
        raise ValueError("Empty DataFrame provided")
        
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            if df.empty:
                raise ValueError(f"No messages found for user: {selected_user}")

        heatmap_df = df.pivot_table(
            index='day_name',
            columns='period',
            values='message',
            aggfunc='count',
            fill_value=0
        )
        
        # Ensure consistent ordering
        heatmap_df = heatmap_df.reindex([
            'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        
        return heatmap_df
    except Exception as e:
        raise ValueError(f"Error in activity_heatmap: {str(e)}")