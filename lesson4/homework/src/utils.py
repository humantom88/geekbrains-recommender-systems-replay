import numpy as np


def prefilter_items(data, item_features, n_popular=5000, first_sort_popular=True):
    if first_sort_popular:
        # Left only top n most popular items
        popularity = data.groupby('item_id')['quantity'].count().reset_index()
        popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
        top_n_popular = popularity.sort_values('n_sold', ascending=False).\
                                        head(n_popular).item_id.tolist()
        # Not to loose users
        data.loc[~data['item_id'].isin(top_n_popular), 'item_id'] = 999999
        
    # Remove most popular from recommendation list
    popularity = (data.groupby('item_id')['user_id'].nunique() / data.user_id.nunique()).reset_index() 
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)

    top_popular = popularity[popularity.share_unique_users > 0.2].item_id.tolist()
    data.loc[data['item_id'].isin(top_popular), 'item_id'] = 999999
    
    # Remove most non-popular
    unpopular = popularity[popularity.share_unique_users < 0.02].item_id.tolist()
    data.loc[data['item_id'].isin(unpopular), 'item_id'] = 999999 
    
    # Remove not sold during 12 month
    t = data.week_no.max() - 52
    sold_last_12_month = data[data.week_no >= t].item_id.unique().tolist()
    data.loc[~data['item_id'].isin(sold_last_12_month), 'item_id'] = 999999
    
    # Remove not interesting (department)
    department_size = item_features.groupby('department')['item_id'].nunique().\
                                       sort_values(ascending=False).reset_index()
    department_size.rename(columns={'item_id': 'n_items'}, inplace=True)
    slow_departments = department_size[department_size.n_items < 150].department.tolist()

    items_in_slow_deparmments = item_features[
        item_features.department.isin(slow_departments)].item_id.unique().tolist()
    data.loc[data['item_id'].isin(items_in_slow_deparmments), 'item_id'] = 999999
    
    # Remove cheapest 
    data['price'] = data['sales_value'] / np.maximum(data['quantity'], 1)
    data.loc[data['price'] < 2, 'item_id'] = 999999
    
    # Remove most expensive
    data.loc[data['price'] > 50, 'item_id'] = 999999
    
    if not first_sort_popular:
        # Left only n most popular after the filtration
        popularity = data.groupby('item_id')['quantity'].count().reset_index() #### sum
        popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
        top_n_popular = popularity.sort_values('n_sold', ascending=False).\
                                        head(n_popular).item_id.tolist()
        data.loc[~data['item_id'].isin(top_n_popular), 'item_id'] = 999999
        
    return data


def postfilter_items():
    pass