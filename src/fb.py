import math
import os

from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from datetime import datetime
from geopy.geocoders import Nominatim

con = pymysql.connect(host="localhost", port=3306, user="root", passwd="root", db="travelblog")
cmd = con.cursor()

fb = Flask(__name__)
fb.secret_key = "nokkanda vdf"


@fb.route('/dump', methods=['GET', 'POST'])
def dump():
    if request.method == 'POST':
        file = request.files['vid']
        print(file.filename)
        file.save('static/uploads/' + file.filename)
        return render_template('dump2.html', vid=file.filename)
    else:
        return render_template('dump.html')


@fb.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        name = fname + ' ' + lname
        print(name)
        age = request.form['dob']
        gen = request.form['gender']
        addr = request.form['country']
        email = request.form['email']
        phone = request.form['phone']
        usr = request.form['username']
        password = request.form['password']

        cmd.execute("SELECT * FROM `login` WHERE `username`='" + usr + "' ")
        result = cmd.fetchone()
        print(f" usr result = {result}")
        if result is None:
            cmd.execute("INSERT INTO `login` VALUES(NULL, '" + usr + "', '" + password + "', 'user',0)")
            lid = con.insert_id()
            cmd.execute("INSERT INTO `users` VALUES(NULL, '" + str(lid) + "','" + name + "', '" + age + "', '" + gen + "', '" + addr + "',\
             '" + email + "', '" + phone + "', 'nopfp.jpg')")
            con.commit()
            return "<script>alert('Sign-up Successful');window.location='/'</script>"

        else:
            return "<script>alert('This Username is Already Taken, Please Create a New Username');window.location='/signup_page'</script>"
    else:
        cmd.execute("DELETE FROM `users` WHERE `lid` IS NULL")
        con.commit()
        return render_template('signup.html')


@fb.route('/')
def login_page():
    return render_template('login.html')


@fb.route('/login', methods=['get', 'post'])
def login():
    usr = request.form['uname']
    psswd = request.form['passwd']

    cmd.execute("select * from login where username='" + usr + "' and password='" + psswd + "' ")
    result = cmd.fetchone()
    if result is not None:
        usrtype = result[3]
        if usrtype == 'user':
            session['lid'] = result[0]
            session['usr'] = result[1]
            return redirect(url_for('userHome'))
        elif usrtype == 'admin':
            return redirect(url_for('adminHome'))

    else:
        return "<script>alert('Incorrect Password or Username');window.location='/'</script>"


@fb.route('/userHome')
def userHome():
    lid = session['lid']
    cmd.execute("SELECT `name`,`photo` FROM `users` WHERE `lid`='" + str(lid) + "'")
    acc = cmd.fetchone()
    print(acc)

    # posts
    cmd.execute("SELECT `user_lid` FROM `following` WHERE `login_id`='" + str(lid) + "'")
    res = cmd.fetchall()
    if res:
        lids = [x[0] for x in res]
        lids.append(lid)
        lids = tuple(lids)
    else:
        lids = (lid, 0)
        print(f"else list = {lids}")

    print(lids)

    cmd.execute(f"SELECT `uploads`.*, `users`.`name`,`photo`, `location`,`latitude`,`longitude` \
    FROM `uploads`, `users`, `location` WHERE `uploads`.`user_lid`=`users`.`lid` \
    AND `uploads`.`upload_id`=`location`.`uid` AND  `users`.`lid` IN {lids} ORDER BY `upload_id` DESC")
    result = cmd.fetchall()
    # print(f"old result = {result}")

    # Comments
    cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users` WHERE \
    `comment`.`user_lid`=`users`.`lid` ORDER BY `comment_id` DESC")
    cmnt = cmd.fetchall()
    # print(cmnt)

    if result is not None:
        c = -1
        for i in result:
            c += 1
            result = list(result)

            i = list(i)
            le = len(i)
            # print(i)

            # UPLOAD DATE AND TIME

            uploadTime = datetime.strptime(i[5], "%H:%M:%S")
            # print(f"uploadTime = {uploadTime}")
            uploadDate = i[4]
            # print(f"uploadDate = {uploadDate}")

            # Current Time---->
            now = datetime.now()
            # print(f"now = {now}")
            dt = now.strftime("%Y-%m-%d.%H:%M:%S")
            fsplit = str.split(dt, '.')
            # print(f"fsplit = {fsplit}")
            nowDate = fsplit[0]
            nowTime = datetime.strptime(fsplit[1], "%H:%M:%S")
            # print(f"nowTate = {nowDate} -  {type(nowDate)}, nowTime = {nowTime}-  - {type(nowTime)}")

            if uploadDate == nowDate:
                delta = nowTime - uploadTime
                rem = int(delta.total_seconds())
                if rem < 60:
                    i[5] = str(rem) + " seconds"
                    i.insert(le, 'other')
                else:
                    mins, secs = divmod(rem, 60)
                    if mins < 60:
                        i[5] = str(mins) + " minutes"
                        i.insert(le, 'other')
                    else:
                        hours, mins = divmod(mins, 60)
                        i[5] = str(hours) + " hours"
                        i.insert(le, 'other')
                result[c] = i
                result = tuple(result)
                # print(f"new result ={result}")
            elif uploadDate != nowDate:
                d1 = datetime.strptime(uploadDate, "%Y-%m-%d")
                d2 = datetime.strptime(nowDate, "%Y-%m-%d")
                # print(f'd1 ={d1} d2={d2}')

                # difference between dates in timedelta
                delta1 = d2 - d1
                days = delta1.days
                # print(f' delta1 = {days}')
                if days < 6:
                    i[5] = str(days) + " days"
                    i.insert(le, 'other')
                    result[c] = i
                elif 30 > days > 6:
                    if 14 > days > 7:
                        i[5] = str(1) + " week"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 21 > days > 14:
                        i[5] = str(2) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 28 > days > 21:
                        i[5] = str(3) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 60 > days > 30:
                        i[5] = str(1) + " month"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    else:
                        i.insert(le, 'normal')
                        result[c] = i
                        result = tuple(result)
                else:
                    i.insert(le, 'normal')
                    result[c] = i
                    result = tuple(result)

            else:
                i.insert(le, 'normal')
                result[c] = i
                result = tuple(result)
                # print(f"normal result ={result}")

        print(f"new result ={result}")
        return render_template('userHome.html', res1=result, acc=acc, com=cmnt)
    else:
        return render_template('userHome.html', res1=result, acc=acc, com=cmnt)


@fb.route('/upload', methods=['get', 'post'])
def upload():
    geoLocator = Nominatim(user_agent="geoapiExercises")
    lat = request.form['lat']
    print(lat)
    lon = request.form['lon']

    locDict = geoLocator.reverse(lat + "," + lon)
    loc = locDict.raw['display_name']
    print(loc)

    lid = str(session['lid'])
    usr = session['usr']

    val = request.form['uploadBtn']
    print(val)
    if val == 'photo':
        cap = request.form['caption']
        pfiles = request.files.getlist('photo')
        count = len(pfiles)

        cmd.execute("INSERT INTO `uploads` VALUES(NULL,'"+lid+"','photo','"+cap+"',CURDATE(),CURTIME(), '"+str(count)+"',null,null,'no',0)")
        uid = str(con.insert_id())
        c = 1

        cmd.execute("INSERT INTO `location` VALUES(NULL,'"+uid+"','"+lat+"','"+lon+"','"+loc+"')")
        con.commit()

        for file in pfiles:
            # photo file save to folder
            split = str.split(file.filename, '.')
            ext = '.' + split[len(split) - 1]
            fname = usr + uid
            photo = fname + "-" + str(c) + ext
            file.save('static/uploads/' + photo)
            cmd.execute("INSERT INTO `upload_files` VALUES(NULL, '"+uid+"', '"+photo+"')")
            cmd.execute("UPDATE `uploads` SET `fname`='"+fname+"', `ext`='"+ext+"' WHERE `upload_id`='"+uid+"' ")
            con.commit()
            c += 1

    elif val == 'video':
        cap = request.form['caption1']
        file = request.files['video']

        cmd.execute("INSERT INTO `uploads` VALUES(NULL,'"+lid+"','photo','"+cap+"',CURDATE(),CURTIME(), '10101', null,null,'no',0)")
        uid = str(con.insert_id())

        ext = '.' + str(str.split(file.filename, '.')[-1])
        fname = usr + '_' + uid
        video = fname + ext
        file.save('static/uploads/video/' + video)

        cmd.execute("INSERT INTO `location` VALUES(NULL,'"+uid+"','"+lat+"','"+lon+"','"+loc+"')")

        cmd.execute("INSERT INTO `upload_files` VALUES(NULL, '"+uid+"', '"+video+"')")
        cmd.execute("UPDATE `uploads` SET `fname`='"+fname+"', `ext`='"+ext+"' WHERE `upload_id`='"+uid+"' ")
        con.commit()

    return redirect(url_for('userHome'))


@fb.route('/videoUpload')
def videoUpload():
    return render_template('videoUpload.html')


@fb.route('/home_actions', methods=['GET', 'POST'])
def home_actions():
    lid = str(session['lid'])
    pressed = request.form['pressed']
    print(pressed)
    uid = request.form['uid']
    user_lid = request.form['user_id']
    if pressed == 'comment':
        comment = request.form['comment']
        cmd.execute(
            "INSERT INTO COMMENT VALUES(NULL, '" + lid + "', '" + uid + "', '" + comment + "', CURDATE(), CURTIME())")
        cmd.execute("UPDATE `uploads` SET `comment`='yes' WHERE `upload_id`='" + uid + "' ")
        con.commit()
    elif pressed == 'like':
        cmd.execute("SELECT * FROM `likes` WHERE `uid`='" + uid + "' AND `lid`='" + lid + "' ")
        res = cmd.fetchone()
        if res:
            cmd.execute("SELECT `like` FROM `uploads` WHERE `upload_id`='" + uid + "' ")
            like = int(cmd.fetchone()[0])
            like -= 1
            cmd.execute(f"UPDATE `uploads` SET `like`={like} WHERE `upload_id`={uid}")
            cmd.execute("DELETE FROM `likes` WHERE `uid`='" + uid + "' AND `lid`='" + lid + "' ")
            con.commit()
        else:
            cmd.execute("INSERT INTO `likes` VALUES(NULL, '" + uid + "', '" + lid + "')")
            cmd.execute("SELECT `like` FROM `uploads` WHERE `upload_id`='" + uid + "' ")
            like = int(cmd.fetchone()[0])
            like += 1
            cmd.execute(f"UPDATE `uploads` SET `like`={like} WHERE `upload_id`={uid}")
            con.commit()

    elif pressed == 'report':
        cmd.execute("SELECT `reports` FROM login WHERE `lid`='" + user_lid + "' ")
        rep = int(cmd.fetchone()[0])
        print(rep)
        cmd.execute(
            "SELECT * FROM `reports` WHERE `user_lid`='" + user_lid + "' AND `upload_id`='" + uid + "' AND `reporting_user`='" + lid + "' ")
        v = cmd.fetchall()
        if v:
            print()
            return "<script>alert('You have Already Reported This Post!');window.location='/userHome'</script>"
        else:
            rep += 1
            cmd.execute("UPDATE `login` SET `reports`='" + str(rep) + "' WHERE `lid`='" + user_lid + "'")
            cmd.execute(
                "INSERT INTO `reports` VALUES(NULL, '" + user_lid + "', '" + uid + "', '" + lid + "', CURDATE(), CURTIME())")
            con.commit()

    return redirect(request.referrer)


@fb.route('/searchAccounts', methods=['GET', 'POST'])
def searchAccounts():
    lid = session['lid']
    cmd.execute("SELECT `name`,`photo` FROM `users` WHERE `lid`='" + str(lid) + "'")
    acc = cmd.fetchone()
    if request.method == 'POST':
        prompt = "No Search Result"
        prompt1 = "Check Your Spelling"
        txt = request.form['txt']
        cmd.execute("SELECT `users`.`lid`,`name`,`photo`, `login`.`username` FROM `users`, `login` WHERE\
         `login`.`lid`=`users`.`lid` AND `name` LIKE '%" + txt + "%' ")
        res1 = cmd.fetchall()
        print(f"users = {res1}")
        if not res1:
            cmd.execute("SELECT `users`.`lid`,`name`,`photo`, `login`.`username` FROM `users`, `login` WHERE\
             `login`.`lid`=`users`.`lid` AND `username` LIKE '" + txt + "%'")
            res1 = cmd.fetchall()
            print(f"login = {res1}")
            return render_template('search.html', data=res1, p=prompt, p1=prompt1, user=acc)
        return render_template('search.html', data=res1, user=acc)
    else:
        res1 = None
        return render_template('search.html', data=res1, user=acc)


@fb.route('/my_profile/<view>')
def profile_page(view):
    lid = session['lid']
    cmd.execute(
        "SELECT `name`,`photo`,`username` FROM `users`, `login` WHERE `login`.`lid`=`users`.`lid` AND `login`.`lid`='" + str(
            lid) + "'")
    result = cmd.fetchone()
    print(result)

    #  Followers/Following
    cmd.execute("SELECT `users`.`lid`,`name`,`photo`,`username` FROM `following`, `users`, `login` \
    WHERE `following`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='" + str(lid) + "'")
    following = cmd.fetchall()
    # print(F"following = {following}")
    followingCount = len(following)

    cmd.execute("SELECT  `users`.`lid`,`name`,`photo`, `login`.`username` FROM `followers`, `users`, `login` \
    WHERE `followers`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='" + str(lid) + "'")
    followers = cmd.fetchall()
    followersCount = len(followers)
    # print(f"followersCount = {followersCount}")

    # post count
    cmd.execute("SELECT COUNT(`fname`) FROM `uploads` WHERE `user_lid`='" + str(lid) + "'")
    postCount = cmd.fetchone()[0]
    # print(f"post count = {postCount}")

    rowCount = math.ceil(postCount / 3)
    # print(f"row Count = {rowCount}")

    # posts
    cmd.execute("SELECT `uploads`.*, `users`.name,photo, location,latitude,longitude FROM `uploads`,`users`,`location`\
    WHERE `uploads`.`user_lid`=`users`.`lid` AND `uploads`.`upload_id`=`location`.`uid` \
    AND `uploads`.`user_lid`='" + str(lid) + "' ORDER BY `upload_id` DESC ")
    posts = cmd.fetchall()
    print(f"posts = {posts}")

    if view == 'grid':
        return render_template('myprofile-grid.html', user=result, pc=postCount, rc=rowCount, post=posts,
                               fing=following, cfing=followingCount, fer=followers, cfer=followersCount)
    elif view == 'list':
        cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users`, `uploads` \
        WHERE `comment`.`user_lid`=`users`.`lid` AND `comment`.`upload_id`=`uploads`.`upload_id` \
        AND `uploads`.`user_lid`='" + str(lid) + "' ORDER BY `comment_id` DESC")
        cmnt = cmd.fetchall()
        print(cmnt)
        return render_template('myprofile-list.html', user=result, pc=postCount, post=posts, com=cmnt,
                               fing=following, cfing=followingCount, fer=followers, cfer=followersCount)


@fb.route('/editprofile', methods=['get', 'post'])
def editprofile():
    lid = session['lid']
    if request.method == 'POST':
        name = request.form['fname']
        email = request.form['email']
        phone = request.form['phone']

        cmd.execute(
            "UPDATE users SET `name`='" + name + "',`email`='" + email + "',`phone`='" + phone + "' WHERE lid='" + str(
                lid) + "' ")
        con.commit()
        return redirect(url_for('editprofile'))
    else:
        cmd.execute("SELECT `name`,`email`,`phone` FROM `users` WHERE lid='" + str(lid) + "'")
        result = cmd.fetchone()
        return render_template('editprofile.html', data=result)


@fb.route('/pfpSettings/<action>', methods=['GET', 'POST'])
def pfpSettings(action):
    print(action)
    lid = str(session['lid'])
    if action == 'delete':
        cmd.execute("UPDATE `users` SET `photo`='nopfp.jpg' WHERE `lid`='" + lid + "'")
        con.commit()
        print("pfp deleted")
        return redirect(request.referrer)
    elif action == 'upload':
        print("hello")
        p = request.files['photo']
        print(p.filename)
        if p:
            split = os.path.splitext(p.filename)
            ext = split[len(split) - 1]
            pfp = session['usr'] + '-pfp' + ext
            cmd.execute("UPDATE `users` SET `photo`='" + pfp + "' WHERE `lid`='" + lid + "'")
            con.commit()

            if os.path.exists('static/pfp/' + pfp):
                os.remove('static/pfp/' + pfp)
            p.save('static/pfp/' + pfp)

            print("pfp updated")
        return redirect(request.referrer)


@fb.route('/changePasswd', methods=['GET', 'POST'])
def changePasswd():
    lid = str(session['lid'])
    if request.method == 'POST':
        passwd = request.form['pass2']
        cmd.execute("UPDATE `login` SET `password`='" + passwd + "' WHERE `lid`='" + lid + "' ")
        con.commit()
        return redirect('my_profile/grid')
    else:
        return render_template('changePasswd.html')


@fb.route('/changeUsername', methods=['GET', 'POST'])
def changeUsername():
    lid = str(session['lid'])
    if request.method == 'POST':
        username = request.form['uname']
        cmd.execute("SELECT * FROM `login` WHERE `username`='" + username + "' ")
        result = cmd.fetchone()
        if result:
            return "<script>alert('This Username is Taken, Try Another One';window.location='/changeUsername')"
        else:
            cmd.execute("UPDATE `login` SET `username`='" + username + "' WHERE `lid`='" + lid + "' ")
            con.commit()
            return redirect('my_profile/grid')
    else:
        return render_template('changeUsername.html')


@fb.route('/deleteComment/<cid>/<uid>')
def deleteComment(cid,uid):
    print(cid, uid)
    cmd.execute("SELECT * FROM `comment` WHERE `upload_id`='" + uid + "' ")
    res = cmd.fetchall()
    print(res)
    if len(res) == 1:
        print("yes")
        cmd.execute("UPDATE `uploads` SET `comment`='no' WHERE `upload_id`='" + uid + "' ")

    cmd.execute("DELETE FROM `comment` WHERE `comment_id`='"+cid+"' ")
    con.commit()

    return redirect(request.referrer)


@fb.route('/userProfile/<uid>', methods=['GET', 'POST'])
def userProfile(uid):
    lid = str(session['lid'])
    if uid == lid:
        return redirect('/my_profile/grid')
    if request.method == "POST":
        pressed = request.form['pressed']
        print(pressed)
        upload_id = request.form['uid']
        if pressed == 'comment':
            comment = request.form['comment']
            cmd.execute("INSERT INTO COMMENT VALUES(NULL, '"+lid+"', '"+upload_id+"', '"+comment+"', CURDATE(), CURTIME())")
            cmd.execute("UPDATE `uploads` SET `comment`='yes' WHERE `upload_id`='"+upload_id+"' ")
            con.commit()

        elif pressed == 'like':
            cmd.execute("SELECT * FROM `likes` WHERE `uid`='"+upload_id+"' AND `lid`='"+lid+"' ")
            liked = cmd.fetchone()
            print(liked)
            if liked:
                cmd.execute("SELECT `like` FROM `uploads` WHERE `upload_id`='"+upload_id+"' ")
                like = int(cmd.fetchone()[0])
                print("likes = ",like)
                like -= 1
                print("new likes = ",like)
                cmd.execute(f"UPDATE `uploads` SET `like`={like} WHERE `upload_id`={upload_id}")
                cmd.execute("DELETE FROM `likes` WHERE `uid`='"+upload_id+"' AND `lid`='"+lid+"' ")
                con.commit()
            else:
                cmd.execute("INSERT INTO `likes` VALUES(NULL, '"+upload_id+"', '"+lid+"')")
                cmd.execute("SELECT `like` FROM `uploads` WHERE `upload_id`='"+upload_id+"' ")
                like = int(cmd.fetchone()[0])
                print("likes = ",like)
                like += 1
                print("new + likes = ",like)
                cmd.execute(f"UPDATE `uploads` SET `like`={like} WHERE `upload_id`={upload_id}")
                con.commit()

        elif pressed == 'report':
            cmd.execute("SELECT `reports` FROM login WHERE `lid`='" + uid + "' ")
            rep = int(cmd.fetchone()[0])
            print(rep)
            cmd.execute("SELECT * FROM `reports` WHERE `user_lid`='"+uid+"' AND `upload_id`='"+upload_id+"' AND `reporting_user`='"+lid+"' ")
            v = cmd.fetchall()
            if v:
                return f"<script>alert('You have Already Reported This Post!');window.location='/userProfile/{uid}'</script>"
            else:
                rep += 1
                cmd.execute("UPDATE `login` SET `reports`='"+str(rep)+"' WHERE `lid`='"+uid+"'")
                cmd.execute("INSERT INTO `reports` VALUES(NULL, '"+uid+"', '"+upload_id+"', '"+lid+"', CURDATE(), CURTIME())")
                con.commit()
        return redirect(f'/userProfile/{uid}')
    else:
        # current user
        cmd.execute("SELECT `name`,`photo`,`username` FROM `users`, `login` WHERE `login`.`lid`=`users`.`lid` \
        AND `login`.`lid`='" + str(lid) + "'")
        res = cmd.fetchone()

        # profile owner
        cmd.execute("SELECT `name`,`photo`,`username`,`login`.`lid` FROM `users`, `login` WHERE \
        `login`.`lid`=`users`.`lid` AND `login`.`lid`='" + uid + "'")
        acc = cmd.fetchone()

        # posts
        cmd.execute("SELECT `users`.`lid`,`name`,`photo`,`username` FROM `following`, `users`, `login` \
        WHERE `following`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='" + uid + "'")
        followings = cmd.fetchall()
        followingCount = len(followings)

        cmd.execute("SELECT * FROM `following` WHERE `login_id`='" + lid + "' AND `user_lid`='" + uid + "' ")
        following = cmd.fetchone()

        cmd.execute("SELECT * FROM `followers` WHERE `login_id`='" + lid + "' AND `user_lid`='" + uid + "' ")
        follower = cmd.fetchone()

        cmd.execute("SELECT  `users`.`lid`,`name`,`photo`, `login`.`username` FROM `followers`, `users`, `login` \
        WHERE `followers`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='" + uid + "'")
        followers = cmd.fetchall()
        followersCount = len(followers)

        cmd.execute("SELECT `uploads`.*, `users`.`name`,`photo`, `location`,`latitude`,`longitude`\
        FROM `uploads`, `users`, `location` WHERE `uploads`.`user_lid`=`users`.`lid`\
        AND `uploads`.`upload_id`=`location`.`uid` AND `uploads`.`user_lid`='" + uid + "' ORDER BY `upload_id` DESC ")
        result = cmd.fetchall()
        postCount = len(result)

        # Comments
        cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users` WHERE \
        `comment`.`user_lid`=`users`.`lid` ORDER BY `comment_id` DESC")
        cmnt = cmd.fetchall()
        # print(cmnt)

        if result is not None:
            c = -1
            for i in result:
                c += 1
                result = list(result)

                i = list(i)
                le = len(i)
                # print(i)

                # UPLOAD DATE AND TIME

                uploadTime = datetime.strptime(i[5], "%H:%M:%S")
                # print(f"uploadTime = {uploadTime}")
                uploadDate = i[4]
                # print(f"uploadDate = {uploadDate}")

                # Current Time---->
                now = datetime.now()
                # print(f"now = {now}")
                dt = now.strftime("%Y-%m-%d.%H:%M:%S")
                fsplit = str.split(dt, '.')
                # print(f"fsplit = {fsplit}")
                nowDate = fsplit[0]
                nowTime = datetime.strptime(fsplit[1], "%H:%M:%S")
                # print(f"nowTate = {nowDate} -  {type(nowDate)}, nowTime = {nowTime}-  - {type(nowTime)}")

                if uploadDate == nowDate:
                    delta = nowTime - uploadTime
                    rem = int(delta.total_seconds())
                    if rem < 60:
                        i[5] = str(rem) + " seconds"
                        i.insert(le, 'other')
                    else:
                        mins, secs = divmod(rem, 60)
                        if mins < 60:
                            i[5] = str(mins) + " minutes"
                            i.insert(le, 'other')
                        else:
                            hours, mins = divmod(mins, 60)
                            i[5] = str(hours) + " hours"
                            i.insert(le, 'other')
                    result[c] = i
                    result = tuple(result)
                    # print(f"new result ={result}")
                elif uploadDate != nowDate:
                    d1 = datetime.strptime(uploadDate, "%Y-%m-%d")
                    d2 = datetime.strptime(nowDate, "%Y-%m-%d")
                    # print(f'd1 ={d1} d2={d2}')

                    # difference between dates in timedelta
                    delta1 = d2 - d1
                    days = delta1.days
                    # print(f' delta1 = {days}')
                    if days < 6:
                        i[5] = str(days) + " days"
                        i.insert(le, 'other')
                        result[c] = i
                    elif 30 > days > 6:
                        if 14 > days > 7:
                            i[5] = str(1) + " week"
                            i.insert(le, 'other')
                            result[c] = i
                            result = tuple(result)
                        elif 21 > days > 14:
                            i[5] = str(2) + " weeks"
                            i.insert(le, 'other')
                            result[c] = i
                            result = tuple(result)
                        elif 28 > days > 21:
                            i[5] = str(3) + " weeks"
                            i.insert(le, 'other')
                            result[c] = i
                            result = tuple(result)
                        elif 60 > days > 30:
                            i[5] = str(1) + " month"
                            i.insert(le, 'other')
                            result[c] = i
                            result = tuple(result)
                        else:
                            i.insert(le, 'normal')
                            result[c] = i
                            result = tuple(result)
                    else:
                        i.insert(le, 'normal')
                        result[c] = i
                        result = tuple(result)

                else:
                    i.insert(le, 'normal')
                    result[c] = i
                    result = tuple(result)
                    # print(f"normal result ={result}")

            print(f"new result ={result}")
        return render_template('userprofile.html', cuser=res, acc=acc, res1=result, pc=postCount, following=following,
                               follower=follower, fing=followings, cfing=followingCount,
                               fer=followers, cfer=followersCount, com=cmnt)


@fb.route('/follow/<uid>')
def follow(uid):
    lid = session['lid']
    cmd.execute("SELECT * FROM `following` WHERE `login_id`='"+str(lid)+"' AND `user_lid`='"+str(uid)+"'")
    res = cmd.fetchone()
    if res:
        return redirect(request.referrer)
    else:
        cmd.execute("INSERT INTO `following` VALUES(NULL, '"+str(lid)+"', '"+str(uid)+"')")
        cmd.execute("INSERT INTO `followers` VALUES(NULL, '"+str(uid)+"', '"+str(lid)+"')")
        con.commit()
        return redirect(request.referrer)


@fb.route('/unfollow/<uid>')
def unfollow(uid):
    print("unfollow", uid, type(uid))
    lid = session['lid']
    cmd.execute("DELETE FROM `following` WHERE `login_id`='"+str(lid)+"' AND `user_lid`='"+uid+"' ")
    cmd.execute("DELETE FROM `followers` WHERE `login_id`='"+uid+"' AND `user_lid`='"+str(lid)+"' ")
    con.commit()
    return redirect(request.referrer)


# -------------------------- Admin ----------------------------------
@fb.route('/adminHome')
def adminHome():
    cmd.execute("SELECT `uploads`.*, `users`.`name`,`photo`, `location`,`latitude`,`longitude`\
    FROM `uploads`, `location`,`login`,`users` WHERE `uploads`.`upload_id`=`location`.`uid`\
    AND  `uploads`.`user_lid`=`login`.`lid` AND `uploads`.`user_lid`=`users`.`lid` ORDER BY `upload_id` DESC")
    result = cmd.fetchall()

    print(result)

    cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users` WHERE \
    `comment`.`user_lid`=`users`.`lid` ORDER BY `comment_id` DESC")
    cmnt = cmd.fetchall()

    if result is not None:
        c = -1
        for i in result:
            c += 1
            result = list(result)

            i = list(i)
            le = len(i)
            # print(i)

            # UPLOAD DATE AND TIME

            uploadTime = datetime.strptime(i[5], "%H:%M:%S")
            # print(f"uploadTime = {uploadTime}")
            uploadDate = i[4]
            # print(f"uploadDate = {uploadDate}")

            # Current Time---->
            now = datetime.now()
            # print(f"now = {now}")
            dt = now.strftime("%Y-%m-%d.%H:%M:%S")
            fsplit = str.split(dt, '.')
            # print(f"fsplit = {fsplit}")
            nowDate = fsplit[0]
            nowTime = datetime.strptime(fsplit[1], "%H:%M:%S")
            # print(f"nowTate = {nowDate} -  {type(nowDate)}, nowTime = {nowTime}-  - {type(nowTime)}")

            if uploadDate == nowDate:
                delta = nowTime - uploadTime
                rem = int(delta.total_seconds())
                if rem < 60:
                    i[5] = str(rem) + " seconds"
                    i.insert(le, 'other')
                else:
                    mins, secs = divmod(rem, 60)
                    if mins < 60:
                        i[5] = str(mins) + " minutes"
                        i.insert(le, 'other')
                    else:
                        hours, mins = divmod(mins, 60)
                        i[5] = str(hours) + " hours"
                        i.insert(le, 'other')
                result[c] = i
                result = tuple(result)
                # print(f"new result ={result}")
            elif uploadDate != nowDate:
                d1 = datetime.strptime(uploadDate, "%Y-%m-%d")
                d2 = datetime.strptime(nowDate, "%Y-%m-%d")
                # print(f'd1 ={d1} d2={d2}')

                # difference between dates in timedelta
                delta1 = d2 - d1
                days = delta1.days
                # print(f' delta1 = {days}')
                if days < 6:
                    i[5] = str(days) + " days"
                    i.insert(le, 'other')
                    result[c] = i
                elif 30 > days > 6:
                    if 14 > days > 7:
                        i[5] = str(1) + " week"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 21 > days > 14:
                        i[5] = str(2) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 28 > days > 21:
                        i[5] = str(3) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 60 > days > 30:
                        i[5] = str(1) + " month"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    else:
                        i.insert(le, 'normal')
                        result[c] = i
                        result = tuple(result)
                else:
                    i.insert(le, 'normal')
                    result[c] = i
                    result = tuple(result)

            else:
                i.insert(le, 'normal')
                result[c] = i
                result = tuple(result)
                # print(f"normal result ={result}")

        print(f"new result ={result}")
        return render_template('adminHome.html', res=result, com=cmnt)
    else:
        return render_template('adminHome.html', res=result, com=cmnt)


@fb.route('/adminUserList', methods=['GET', 'POST'])
def adminUserList():
    if request.method == 'POST':
        prompt = "No Search Result"
        prompt1 = "Check Your Spelling"
        txt = request.form['txt']
        print(txt)
        cmd.execute("SELECT `login`.`lid`,`username`, `users`.`name`,`photo` FROM `users`,`login` \
        WHERE `login`.`lid`=`users`.`lid` AND `name` LIKE '%" + txt + "%' ")
        res1 = cmd.fetchall()
        print(f"name = {res1}")

        if not res1:
            cmd.execute("SELECT `login`.`lid`,`username`, `users`.`name`,`photo` FROM `users`,`login` \
            WHERE `login`.`lid`=`users`.`lid` AND `username` LIKE '" + txt + "%'")
            res1 = cmd.fetchall()
            print(f"username = {res1}")
            return render_template('admin-users.html', data=res1, p=prompt, p1=prompt1)
        return render_template('admin-users.html', data=res1)
    else:
        cmd.execute("SELECT `login`.`lid`,`username`, `users`.`name`,`photo` FROM `users`,`login` \
        WHERE `login`.`lid`=`users`.`lid` AND `login`.`lid`!=1")
        result = cmd.fetchall()
        print(f"result = {result}")
        return render_template('admin-users.html', data=result)


@fb.route('/removePost/<uid>')
def removePost(uid):
    cmd.execute("SELECT `ext` FROM `uploads` WHERE `upload_id`='"+uid+"'")
    ext = cmd.fetchone()[0]
    if ext.lower() == '.jpeg' or ext.lower() == '.jpg' or ext.lower() == '.png':
        cmd.execute("SELECT `filename` FROM `upload_files` WHERE `uid`='"+uid+"'")
        files = cmd.fetchall()
        print(files)
        for i in files:
            os.remove('static/uploads/' + i[0])
    elif ext.lower() == '.mp4':
        cmd.execute("SELECT `filename` FROM `upload_files` WHERE `uid`='"+uid+"'")
        file = cmd.fetchone()[0]
        os.remove('static/uploads/video/' + file)

    cmd.execute("DELETE u, uf FROM uploads AS u JOIN upload_files AS uf ON uf.uid=u.upload_id WHERE u.upload_id='"+uid+"'")
    cmd.execute("DELETE FROM `location` WHERE `uid`='"+uid+"' ")
    cmd.execute("DELETE FROM `comment` WHERE `upload_id`='" + uid + "' ")
    con.commit()
    print("deleted")
    return redirect(request.referrer)


@fb.route('/adminSearch', methods=['GET', 'POST'])
def adminSearch():
    if request.method == 'POST':
        prompt = "No Search Result"
        prompt1 = "Check Your Spelling"
        txt = request.form['txt']
        cmd.execute("SELECT `users`.`lid`,`name`,`photo`, `login`.`username` FROM `users`, `login` WHERE\
         `login`.`lid`=`users`.`lid` AND `name` LIKE '%" + txt + "%' ")
        res1 = cmd.fetchall()
        print(f"users = {res1}")
        if not res1:
            cmd.execute("SELECT `users`.`lid`,`name`,`photo`, `login`.`username` FROM `users`, `login` WHERE\
             `login`.`lid`=`users`.`lid` AND `username` LIKE '" + txt + "%'")
            res1 = cmd.fetchall()
            print(f"login = {res1}")
            return render_template('admin-search.html', data=res1, p=prompt, p1=prompt1)
        return render_template('admin-search.html', data=res1)
    else:
        res1 = None
        return render_template('admin-search.html', data=res1)


@fb.route('/admin-userprofile/<pid>')
def admin_profile(pid):
    print(f"login id : {pid}")

    cmd.execute("SELECT `name`,`photo`,`username`,`login`.`lid` FROM `users`, `login` WHERE `login`.`lid`=`users`.`lid` \
    AND `login`.`lid`='"+pid+"'")
    res = cmd.fetchone()
    print(f"user = {res}")

    cmd.execute("SELECT `uploads`.*,`location`,`latitude`,`longitude` FROM `uploads`, `location` \
    WHERE `uploads`.`upload_id`=`location`.`uid` AND `uploads`.`user_lid`='"+pid+"' ORDER BY `upload_id` DESC")
    result = cmd.fetchall()
    postCount = len(result)

    #  Followers/Following
    cmd.execute("SELECT `users`.`lid`,`name`,`photo`,`username` FROM `following`, `users`, `login` \
    WHERE `following`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='" + pid + "'")
    followings = cmd.fetchall()
    followingCount = len(followings)

    cmd.execute("SELECT  `users`.`lid`,`name`,`photo`, `login`.`username` FROM `followers`, `users`, `login` \
    WHERE `followers`.`user_lid`=`users`.`lid` AND `login`.`lid`=`users`.`lid` AND `login_id`='"+pid+"'")
    followers = cmd.fetchall()
    followersCount = len(followers)

    cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users` \
    WHERE `comment`.`user_lid`=`users`.`lid` AND `comment`.`user_lid`='"+pid+"' ORDER BY `comment_id` DESC")
    cmnt = cmd.fetchall()

    cmd.execute("SELECT `reports` FROM `login` WHERE lid='"+pid+"' ")
    reps = cmd.fetchone()[0]
    print(reps)

    if result:
        c = -1
        for i in result:
            c += 1
            result = list(result)

            i = list(i)
            le = len(i)
            # print(i)

            # UPLOAD DATE AND TIME

            uploadTime = datetime.strptime(i[5], "%H:%M:%S")
            # print(f"uploadTime = {uploadTime}")
            uploadDate = i[4]
            # print(f"uploadDate = {uploadDate}")

            # Current Time---->
            now = datetime.now()
            # print(f"now = {now}")
            dt = now.strftime("%Y-%m-%d.%H:%M:%S")
            fsplit = str.split(dt, '.')
            # print(f"fsplit = {fsplit}")
            nowDate = fsplit[0]
            nowTime = datetime.strptime(fsplit[1], "%H:%M:%S")
            # print(f"nowTate = {nowDate} -  {type(nowDate)}, nowTime = {nowTime}-  - {type(nowTime)}")

            if uploadDate == nowDate:
                delta = nowTime - uploadTime
                rem = int(delta.total_seconds())
                if rem < 60:
                    i[5] = str(rem) + " seconds"
                    i.insert(le, 'other')
                else:
                    mins, secs = divmod(rem, 60)
                    if mins < 60:
                        i[5] = str(mins) + " minutes"
                        i.insert(le, 'other')
                    else:
                        hours, mins = divmod(mins, 60)
                        i[5] = str(hours) + " hours"
                        i.insert(le, 'other')
                result[c] = i
                result = tuple(result)
                # print(f"new result ={result}")
            elif uploadDate != nowDate:
                d1 = datetime.strptime(uploadDate, "%Y-%m-%d")
                d2 = datetime.strptime(nowDate, "%Y-%m-%d")
                # print(f'd1 ={d1} d2={d2}')

                # difference between dates in timedelta
                delta1 = d2 - d1
                days = delta1.days
                # print(f' delta1 = {days}')
                if days < 6:
                    i[5] = str(days) + " days"
                    i.insert(le, 'other')
                    result[c] = i
                elif 30 > days > 6:
                    if 14 > days > 7:
                        i[5] = str(1) + " week"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 21 > days > 14:
                        i[5] = str(2) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 28 > days > 21:
                        i[5] = str(3) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 60 > days > 30:
                        i[5] = str(1) + " month"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    else:
                        i.insert(le, 'normal')
                        result[c] = i
                        result = tuple(result)
                else:
                    i.insert(le, 'normal')
                    result[c] = i
                    result = tuple(result)

            else:
                i.insert(le, 'normal')
                result[c] = i
                result = tuple(result)
                # print(f"normal result ={result}")

        print(f"new result ={result}")
        return render_template('admin-userprofile.html', res1=result, user=res, pc=postCount, fing=followings,
                               cfing=followingCount, fer=followers, cfer=followersCount, com=cmnt, rep=reps)
    else:
        result = None
        return render_template('admin-userprofile.html', res1=result, user=res, pc=postCount, fing=followings,
                               cfing=followingCount, fer=followers, cfer=followersCount, com=cmnt, rep=reps)


@fb.route('/removeAcc/<lid>')
def removeAcc(lid):
    print("remove?", lid)

    cmd.execute("SELECT upload_id FROM uploads WHERE user_lid='"+lid+"'")
    uids = [i[0] for i in cmd.fetchall()]
    if uids:
        uids.append(0)
        uids = tuple(uids)
    else:
        uids = (0, 0)
    print(uids)

    cmd.execute(f"SELECT filename,count FROM upload_files,uploads \
    WHERE uploads.upload_id=upload_files.uid AND uid IN {uids}")
    res = cmd.fetchall()

    for i in res:
        if i[1] == '10101':
            os.remove("static/upload/video" + i[0])
        else:
            os.remove("static/uploads/" + i[0])

    cmd.execute("SELECT photo FROM users WHERE lid='"+lid+"'")
    pfp = cmd.fetchone()[0]
    if pfp != 'nopfp.jpg':
        os.remove("static/pfp/" + pfp)

    cmd.execute("DELETE FROM login WHERE lid='"+lid+"'")
    cmd.execute("DELETE FROM users WHERE lid='"+lid+"'")
    cmd.execute(f"DELETE FROM upload_files WHERE uid IN {uids}")
    cmd.execute("DELETE FROM reports WHERE reporting_user OR user_lid='"+lid+"'")
    cmd.execute(f"DELETE FROM reports WHERE upload_id IN {uids} ")
    cmd.execute("DELETE FROM uploads WHERE user_lid='"+lid+"'")
    cmd.execute(f"DELETE FROM likes WHERE uid IN {uids}")
    cmd.execute("DELETE FROM likes WHERE lid='"+lid+"'")
    cmd.execute(f"DELETE FROM location WHERE uid IN {uids}")
    cmd.execute("DELETE FROM following WHERE login_id OR user_lid='"+lid+"'")
    cmd.execute("DELETE FROM followers WHERE login_id OR user_lid='"+lid+"'")
    cmd.execute(f"DELETE FROM comment WHERE upload_id IN {uids}")
    cmd.execute("DELETE FROM comment WHERE user_lid='"+lid+"'")

    con.commit()
    return redirect(url_for('adminUserList'))


@fb.route('/reportPosts')
def reportPosts():
    cmd.execute("SELECT `uploads`.*, `users`.`name`,`photo`, `location`,`latitude`,`longitude`\
    FROM `uploads`, `location`,`login`,`users`,`reports` WHERE `uploads`.`upload_id`=`location`.`uid`\
    AND  `uploads`.`user_lid`=`login`.`lid` AND `uploads`.`user_lid`=`users`.`lid` \
    AND `uploads`.`upload_id`=`reports`.`upload_id` ORDER BY `reports`.`date` DESC")
    result = cmd.fetchall()

    print(result)

    cmd.execute("SELECT `comment`.*, `users`.`photo`,`name` FROM `comment`, `users` WHERE \
        `comment`.`user_lid`=`users`.`lid` ORDER BY `comment_id` DESC")
    cmnt = cmd.fetchall()

    if result is not None:
        c = -1
        for i in result:
            c += 1
            result = list(result)

            i = list(i)
            le = len(i)
            # print(i)

            # UPLOAD DATE AND TIME

            uploadTime = datetime.strptime(i[5], "%H:%M:%S")
            # print(f"uploadTime = {uploadTime}")
            uploadDate = i[4]
            # print(f"uploadDate = {uploadDate}")

            # Current Time---->
            now = datetime.now()
            # print(f"now = {now}")
            dt = now.strftime("%Y-%m-%d.%H:%M:%S")
            fsplit = str.split(dt, '.')
            # print(f"fsplit = {fsplit}")
            nowDate = fsplit[0]
            nowTime = datetime.strptime(fsplit[1], "%H:%M:%S")
            # print(f"nowTate = {nowDate} -  {type(nowDate)}, nowTime = {nowTime}-  - {type(nowTime)}")

            if uploadDate == nowDate:
                delta = nowTime - uploadTime
                rem = int(delta.total_seconds())
                if rem < 60:
                    i[5] = str(rem) + " seconds"
                    i.insert(le, 'other')
                else:
                    mins, secs = divmod(rem, 60)
                    if mins < 60:
                        i[5] = str(mins) + " minutes"
                        i.insert(le, 'other')
                    else:
                        hours, mins = divmod(mins, 60)
                        i[5] = str(hours) + " hours"
                        i.insert(le, 'other')
                result[c] = i
                result = tuple(result)
                # print(f"new result ={result}")
            elif uploadDate != nowDate:
                d1 = datetime.strptime(uploadDate, "%Y-%m-%d")
                d2 = datetime.strptime(nowDate, "%Y-%m-%d")
                # print(f'd1 ={d1} d2={d2}')

                # difference between dates in timedelta
                delta1 = d2 - d1
                days = delta1.days
                # print(f' delta1 = {days}')
                if days < 6:
                    i[5] = str(days) + " days"
                    i.insert(le, 'other')
                    result[c] = i
                elif 30 > days > 6:
                    if 14 > days > 7:
                        i[5] = str(1) + " week"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 21 > days > 14:
                        i[5] = str(2) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 28 > days > 21:
                        i[5] = str(3) + " weeks"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    elif 60 > days > 30:
                        i[5] = str(1) + " month"
                        i.insert(le, 'other')
                        result[c] = i
                        result = tuple(result)
                    else:
                        i.insert(le, 'normal')
                        result[c] = i
                        result = tuple(result)
                else:
                    i.insert(le, 'normal')
                    result[c] = i
                    result = tuple(result)

            else:
                i.insert(le, 'normal')
                result[c] = i
                result = tuple(result)
                # print(f"normal result ={result}")

        print(f"new result ={result}")
        return render_template('reportPosts.html', res=result, com=cmnt)
    else:
        return render_template('reportPosts.html', res=result, com=cmnt)


if __name__ == "__main__":
    fb.run(debug=True, port=5002)
