# -*- encoding: utf8 -*-
from options import db
from datetime import datetime

class Webtoon(db.Model):
    __tablename__ = 'webtoon'

    wid = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(4))
    title = db.Column(db.String(300))
    url = db.Column(db.String(300))
    thumbnail = db.Column(db.String(300))
    site = db.Column(db.String(10))
    updated = db.Column(db.DateTime)
    lastthumb = db.Column(db.String(300))
    lasttitle = db.Column(db.String(256))
    lasturl = db.Column(db.String(300))
    lasturl_m = db.Column(db.String(300))
    titleid = db.Column(db.String(64))
    subscriber = db.Column(db.Integer)
    begin_publish = db.Column(db.DateTime)

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
        dt_from = self.updated if self.updated else self.begin_publish

        if not dt_from: return u'알 수 없음'
        if not dt_until: dt_until = datetime.now()
        delta_seconds = (dt_until - dt_from).total_seconds()
        delta_minutes = delta_seconds / 60
        delta_hours = delta_minutes / 60
        delta_days = delta_hours / 24
        delta_months = delta_days / 30

        if delta_days >= 1.0:
            if delta_days < 2.0: return u'어제'
            elif delta_days < 3.0: return u'그제'
            elif delta_days < 30: return u'%d 일 전' % delta_days
            return u'%d 달 전' % delta_months
        elif delta_hours>=1: return u'%d 시간 전' % delta_hours
        elif delta_minutes>=1: return u'%d 분 전' % delta_minutes
        else: return u'%d 초 전' % delta_seconds

    def days_ago(dt_from):
        return (dt_until - dt_from).days

    def period_updated(self):
        return days_ago(self.updated if self.updated else self.begin_publish)

    def period_publish(self):
        return days_ago(self.begin_publish)

    def __repr__(self):
        form = (self.wid, self.title, self.site)
        return "<Webtoon([%r], [%r], [%r])>" % form

class User(db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.Integer, primary_key=True)
    twitterid = db.Column(db.String(32))
    facebookid = db.Column(db.String(64))
    date_signup = db.Column(db.DateTime)
    date_lastuse = db.Column(db.DateTime)
    username = db.Column(db.String(64))
    oauth_token = db.Column(db.String(200))
    oauth_secret = db.Column(db.String(200))

    def __repr__(self):
        form = (self.uid, self.username)
        return "<User([%r], [%r])>" % form

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

class UserWebtoon(db.Model):
    __tablename__ = 'userwebtoon'

    uwid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    wid = db.Column(db.Integer, db.ForeignKey('webtoon.wid'))
    is_read = db.Column(db.Integer)
    delayed_episodes = db.Column(db.Integer)
    lasturl = db.Column(db.String(300))
    lasturl_m = db.Column(db.String(300))

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
        return "<UserWebtoon([%r], [%r], [%r], [%r])>" % form

class Reply(db.Model):
    __tablename__ = 'replies'

    rid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    username = db.Column(db.String(64))
    wid = db.Column(db.Integer, db.ForeignKey('webtoon.wid'))
    reply = db.Column(db.String(140))
    date = db.Column(db.DateTime)

    def __init__(self, uid, username, wid, reply):
        self.uid = uid
        self.username = username
        self.wid = wid
        self.reply = reply
        self.date = datetime.now()

    def __repr__(self):
        form = (self.uid, self.username, self.wid, self.reply)
        return "<Reply([%r], [%r], [%r], [%r])>" % form

class Activity(db.Model):
    __tablename__ = 'activities'

    # added(Webtoon) / subscribed(UserWebtoon) / replied(Reply)
    # 0: added, 1: subscribed, 2: replied
    enum = { 'added': 0, 'subscribed': 1, 'replied': 2}

    def __init__(self, wid, event_id, event_type, date=datetime.now()):
        self.wid = wid
        self.event_id = event_id
        self.event_type = event_type
        self.date = date

    aid = db.Column(db.Integer, primary_key=True)
    wid = db.Column(db.Integer, db.ForeignKey('webtoon.wid'))
    event_id = db.Column(db.Integer)
    event_type = db.Column(db.Integer)
    date = db.Column(db.DateTime)

# vim:ts=4:sts=4:sw=4:et:
