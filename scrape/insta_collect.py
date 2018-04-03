"""Collect Instagram image + user info based on .csv input."""

# author: Chris Emmery
# license: GPL-3.0

import json
import os
from time import gmtime, strftime
from glob import glob
import requests
import pandas as pd
from bs4 import BeautifulSoup


def batch_files():
    """List jobs (.csvs without _fixed version) in current directory."""
    files = glob('./**/*.csv')

    done = {f.replace('_fixed.csv', '') for f in files if 'fixed' in f}
    csvs = {c.replace('.csv', '') for c in files if 'fixed' not in c}

    return list(csvs - done)


def parse_json_header(soup):
    """Fetch Instagram JSON object from HTML header."""
    raw_js = [x.text for x in soup.find_all('script')
              if 'window._sharedData' in x.text][0]
    clean_js = raw_js.replace('window._sharedData = ', '').replace(';', '')
    jsf = json.loads(clean_js)
    return jsf


def get_insta_soup(url):
    """Fetch page and ignore not available ones."""
    page = requests.get(url)
    if page.status_code != '404':
        soup = BeautifulSoup(page.content, "html5lib")
        error = soup.find('h2')
        if not error:
            return soup


def get_img_info(img_jsf):
    """Get graph info for image post."""
    jsfs = img_jsf['entry_data']['PostPage'][0]['graphql']['shortcode_media']

    post_likes = jsfs['edge_media_preview_like']['count']
    post_img = jsfs['display_url']
    post_user = jsfs['owner']['username']

    post_comments = []
    for comment in jsfs['edge_media_to_comment']['edges']:
        post_comments.append(comment['node']['owner']['username'] + ' ' +
                             comment['node']['text'])

    return dict(img=post_img, user=post_user, likes=post_likes,
                comments=post_comments)


def get_usr_info(user_jsf):
    """Get graph info for post owner."""
    jsfs = user_jsf['entry_data']['ProfilePage'][0]['graphql']['user']

    user_activity = jsfs['edge_owner_to_timeline_media']['count']
    user_followers = jsfs['edge_followed_by']['count']
    user_follows = jsfs['edge_follow']['count']

    return dict(activity=user_activity, followers=user_followers,
                follows=user_follows)


def main():
    """Call general collection."""
    for data_dir in batch_files():
        print("Processing", data_dir, "...")

        # read data, drop duplicates, make directory for saving
        data = pd.read_csv('./' + data_dir + '.csv', encoding='utf-8', sep=';')
        data = data.drop_duplicates('url')
        os.makedirs(data_dir, exist_ok=True)

        img_data = {}

        # NOTE: script assumes URLs for the images are in a 'url' column
        for i, url in enumerate(data['url']):
            print(strftime('%H:%M:%S', gmtime()), ':',
                  i + 1, '/', len(data['url']), url)

            _id = url.split('/')[-2]
            try:
                img_soup = get_insta_soup(url)

                if img_soup:  # collect image data
                    img_info = get_img_info(parse_json_header(img_soup))
                    cmt = img_info.pop('comments')  # stored in separate file
                    img_data[i] = img_info
                else:
                    continue

                user_soup = get_insta_soup('https://instagram.com/' +
                                           img_info['user'])

                if user_soup:  # collect user data
                    user_info = get_usr_info(parse_json_header(user_soup))
                    usrf_dir = './{0}/{1}_{2}.txt'.format(
                        data_dir, img_info['user'], _id)

                    # write user info to file
                    with open(usrf_dir, 'w') as usrf:
                        usrc = [k + ' = ' + str(v) for k, v in
                                sorted(user_info.items(), key=lambda x: x[0])]
                        usrf.write("\n".join(usrc))

            except Exception as errm:  # captures SSL flood and other quirks
                print("Error:", str(errm))
                continue

            # write image to file
            with open('./{0}/{1}_{2}.jpg'.format(
                    data_dir, img_info['user'], _id), 'wb') as imgf:
                imgf.write(requests.get(img_info['img']).content)

            if cmt:
                # write comments to file
                with open(usrf_dir.replace('.txt', '_cmt.txt'), 'w') as cf:
                    cf.write("\n".join(cmt))

        # append new file-specific info to data and save
        data = data.join(pd.DataFrame.from_dict(img_data, orient='index'))
        data.to_csv(open('./' + data_dir + '_fixed.csv', 'w'))


if __name__ == '__main__':
    main()
