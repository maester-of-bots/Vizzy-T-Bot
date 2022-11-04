import tweepy



def main():
    api = create_api(API_SECRET, API_KEY, ACCESS_TOKEN, ACCESS_SECRET)
    with open('created_since_id.txt', 'r') as f:
        read_id = f.read()
    latest_id_after_process = read_id
    while True:
        logger.info("new id is {}".format(latest_id_after_process))
        latest_id_after_process = get_tweets(api, "make a list", latest_id_after_process)
        with open('created_since_id.txt', 'w') as txt:
            txt.write(str(latest_id_after_process))
        logger.info("Waiting...")
        time.sleep(60)


main()