from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def days_ago(dt_from, dt_until=datetime.now()):
    return (dt_until - dt_from).days


def readable_delta(dt_from, dt_until=None):
    if not dt_from: return '알 수 없음'
    if not dt_until: dt_until = datetime.now()
    delta_seconds = (dt_until - dt_from).total_seconds()
    delta_minutes = delta_seconds / 60
    delta_hours = delta_minutes / 60
    delta_days = delta_hours / 24
    delta_months = delta_days / 30
    delta_years = delta_days / 365

    if delta_days >= 1.0:
        if delta_days < 2.0: return '어제'
        elif delta_days < 3.0: return '그제'
        elif delta_days < 30: return '{} 일 전'.format(delta_days)
        elif delta_days < 365: return '{} 달 전'.format(delta_months)
        return '{} 년 전'.format(delta_years)
    elif delta_hours>=1: return '{} 시간 전'.format(delta_hours)
    elif delta_minutes>=1: return '{} 분 전'.format(delta_minutes)
    else: return '{} 초 전'.format(delta_seconds)


def is_too_old(ts):
    now = datetime.now()
    return (now-ts).days > 14 # TODO: magic number!


class Webtoon(Base):
    __tablename__ = 'webtoons'

    wid = Column(Integer, primary_key=True)
    day = Column(String(4))
    title = Column(String(300))
    url = Column(String(300))
    thumbnail = Column(String(300))
    site = Column(String(10))
    updated = Column(DateTime)
    lastthumb = Column(String(300))
    lasttitle = Column(String(256))
    lasturl = Column(String(300))
    lasturl_m = Column(String(300))
    titleid = Column(String(64))
    subscriber = Column(Integer)
    begin_publish = Column(DateTime)

    userwebtoons = relationship('UserWebtoon', cascade='all, delete-orphan')
    replies = relationship('Reply', cascade='all, delete-orphan')
    activities = relationship('Activity', cascade='all, delete-orphan')

    def __init__(self, day, title, url, thumbnail, site, titleid):
        self.day = day
        self.title = title
        self.url = url
        self.thumbnail = thumbnail
        self.site = site
        self.updated = datetime.now()
        self.titleid = titleid
        self.subscriber = 0
        self.begin_publish = datetime.now()


    def readable_date(self):
        return readable_delta(self.updated if self.updated else self.begin_publish)

    def period_updated(self):
        return days_ago(self.updated if self.updated else self.begin_publish)

    def period_publish(self):
        return days_ago(self.begin_publish)

    def __repr__(self):
        form = (self.wid, self.title, self.site)
        return "<Webtoon([%s], [%s], [%s])>" % form


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    twitterid = Column(String(32))
    facebookid = Column(String(64))
    date_signup = Column(DateTime)
    date_lastuse = Column(DateTime)
    username = Column(String(64))
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))

    userwebtoons = relationship('UserWebtoon', cascade='all, delete-orphan')
    replies = relationship('Reply', cascade='all, delete-orphan')
    activities = relationship('Activity', cascade='all, delete-orphan')

    def __repr__(self):
        form = (self.uid, self.username)
        return '<User([%s], [%s])>' % form

    def get_id(self):
        return self.wid

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __init__(self, username, twitterid, facebookid, oauth_token, oauth_secret):
        self.username = username
        self.twitterid = twitterid
        self.facebookid = facebookid
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret
        self.date_signup = datetime.now()

class UserWebtoon(Base):
    __tablename__ = 'userwebtoons'

    uwid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('user.uid'))
    wid = Column(Integer, ForeignKey('webtoon.wid'))
    is_read = Column(Integer)
    delayed_episodes = Column(Integer)
    lasturl = Column(String(300))
    lasturl_m = Column(String(300))

    def __init__(self, uid, wid, is_read=False, lasturl=None, delayed_episodes=0):
        self.uid = uid
        self.wid = wid
        self.is_read = is_read
        self.lasturl = lasturl
        self.delayed_episodes = delayed_episodes

    def read(self, url):
        self.is_read = 1
        self.delayed_episodes = 0
        self.lasturl = url

    def updated(self, new_url, new_url_m=None):
        if (self.is_read == 1):
            self.is_read = 0
            self.delayed_episodes = 1
            self.lasturl = new_url
            self.lasturl_m = new_url_m
        else:
            self.delayed_episodes += 1

    def __repr__(self):
        form = (self.uwid, self.uid, self.wid, self.delayed_episodes)
        return "<UserWebtoon([%s], [%s], [%s], [%s])>" % form

class Reply(Base):
    __tablename__ = 'replies'

    rid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey('user.uid'))
    username = Column(String(64))
    wid = Column(Integer, ForeignKey('webtoon.wid'))
    reply = Column(String(140))
    date = Column(DateTime)

    def __init__(self, uid, username, wid, reply):
        self.uid = uid
        self.username = username
        self.wid = wid
        self.reply = reply
        self.date = datetime.now()

    def __repr__(self):
        form = (self.uid, self.username, self.wid, self.reply)
        return "<Reply([%s], [%s], [%s], [%s])>" % form

class Activity(Base):
    __tablename__ = 'activities'

    # added(Webtoon) / subscribed(UserWebtoon) / replied(Reply)
    # 0: added, 1: subscribed, 2: replied
    enum = { 'added': 0, 'subscribed': 1, 'replied': 2}

    def __init__(self, wid, event_id, event_type, date=datetime.now()):
        self.wid = wid
        self.event_id = event_id
        self.event_type = event_type
        self.date = date

    aid = Column(Integer, primary_key=True)
    wid = Column(Integer, ForeignKey('webtoon.wid'))
    event_id = Column(Integer)
    event_type = Column(Integer)
    date = Column(DateTime)

# vim:ts=4:sts=4:sw=4:et:
