import datetime as dt
from types import SimpleNamespace

import pandas as pd

from kairos import indeed

POSTING = """
<div itemtype="http://schema.org/JobPosting">
  <h2 class="jobtitle"><a title="{title}" href="/rc/clk?jk={jk}">{title}</a></h2>
  <span class="company"><span> {company} </span></span>
  <span class="location">New York, NY</span>
  <table><tr><td class="snip"><nobr>{pay}</nobr></td></tr></table>
  <span class="date">{days}</span>
  {review}
</div>
"""


def page():
    postings = [
        POSTING.format(
            title="Data Scientist",
            jk=1,
            company="Acme",
            pay="$150,000 - $170,000 a year",
            days="3 days ago",
            review='<a title="review" href="/cmp/Acme/reviews">12 reviews</a>',
        ),
        POSTING.format(
            title="ML Engineer",
            jk=2,
            company="Initech",
            pay="$160,000 a year",
            days="1 day ago",
            review="",
        ),
    ]
    return SimpleNamespace(text=f"<html><body>{''.join(postings)}</body></html>")


def test_build_search_url():
    url = indeed.build_search_url("data scientist", "New York, NY")
    assert url == (
        "https://www.indeed.com/jobs?&q=data scientist&l=New York, NY&fromage=last"
    )


def test_posting_frame_parses_each_posting():
    df = indeed.posting_frame(page())
    assert list(df["title"]) == ["Data Scientist", "ML Engineer"]
    assert list(df["company"]) == ["Acme", "Initech"]
    assert list(df["url"]) == ["/rc/clk?jk=1", "/rc/clk?jk=2"]
    assert df.loc[0, "review_url"] == "/cmp/Acme/reviews"
    assert pd.isna(df.loc[1, "review_url"])


def test_posting_frame_splits_pay_range():
    df = indeed.posting_frame(page())
    assert list(df["Min compensation"]) == ["$150,000", "$160,000"]
    assert list(df["Max compensation"]) == ["$170,000", "$160,000"]


def test_posting_frame_dates_postings():
    df = indeed.posting_frame(page())
    today = pd.Timestamp(dt.date.today())
    assert [pd.Timestamp(d) for d in df["date"]] == [
        today - pd.Timedelta(days=3),
        today - pd.Timedelta(days=1),
    ]
