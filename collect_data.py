# Create LoL Patch Dataset

import pandas as pd
import scrape_patch_wiki as spw
from scrape_reddit import Patch

def create_files():
    init = pd.DataFrame()
    init.to_csv('submission_table', mode='w')   
    init.to_csv('comment_table', mode='w')

def main():
    df = spw.main()
    create_files()

    patch_num = len(df.index.values)

    for i in df.index.values:
        print "On patch %s of %s..." % (i+1, patch_num+1)
        patch = Patch(df.ix[i, 'Patch'], df.ix[i, 'Link'])
        submission_table, comment_table = patch.collect_all(root_only=False)
        sub_temp = pd.DataFrame(submission_table)
        comment_temp = pd.DataFrame(comment_table)
        sub_temp.to_csv('submission_table', mode='a', encoding='utf-8', index=False, header=False)
        comment_temp.to_csv('comment_table', mode='a', encoding='utf-8', index=False, header=False)

if __name__ == '__main__':
    main()