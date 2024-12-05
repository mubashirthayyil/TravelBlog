/*
SQLyog Community v13.2.0 (64 bit)
MySQL - 5.1.32-community : Database - travelblog
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`travelblog` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `travelblog`;

/*Table structure for table `comment` */

DROP TABLE IF EXISTS `comment`;

CREATE TABLE `comment` (
  `comment_id` int(15) NOT NULL AUTO_INCREMENT,
  `user_lid` int(15) DEFAULT NULL,
  `upload_id` int(15) DEFAULT NULL,
  `comment` varchar(256) DEFAULT NULL,
  `date` varchar(15) DEFAULT NULL,
  `time` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`comment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `comment` */

insert  into `comment`(`comment_id`,`user_lid`,`upload_id`,`comment`,`date`,`time`) values 
(3,2,9,'hahaha','2023-04-03','05:51:08');

/*Table structure for table `followers` */

DROP TABLE IF EXISTS `followers`;

CREATE TABLE `followers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `user_lid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `followers` */

/*Table structure for table `following` */

DROP TABLE IF EXISTS `following`;

CREATE TABLE `following` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `user_lid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `following` */

/*Table structure for table `likes` */

DROP TABLE IF EXISTS `likes`;

CREATE TABLE `likes` (
  `like_id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `lid` int(11) DEFAULT NULL,
  PRIMARY KEY (`like_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

/*Data for the table `likes` */

insert  into `likes`(`like_id`,`uid`,`lid`) values 
(9,9,2);

/*Table structure for table `location` */

DROP TABLE IF EXISTS `location`;

CREATE TABLE `location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `latitude` varchar(100) DEFAULT NULL,
  `longitude` varchar(100) DEFAULT NULL,
  `location` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

/*Data for the table `location` */

insert  into `location`(`id`,`uid`,`latitude`,`longitude`,`location`) values 
(6,6,'11.040056152240524','75.93203902244568','KC ROAD, Tirurangadi, Malappuram, Kerala, 676306, India'),
(9,9,'10.864893017870347','76.74682723305227','Palakkad, Kerala, India');

/*Table structure for table `login` */

DROP TABLE IF EXISTS `login`;

CREATE TABLE `login` (
  `lid` int(15) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `usertype` varchar(50) DEFAULT NULL,
  `reports` int(50) DEFAULT NULL,
  PRIMARY KEY (`lid`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

/*Data for the table `login` */

insert  into `login`(`lid`,`username`,`password`,`usertype`,`reports`) values 
(1,'admin','admin','admin',0),
(2,'zayan.shamz','489','user',3),
(4,'dada','dada','user',0),
(6,'sith','sith','user',0),
(7,'seee','sith','user',0);

/*Table structure for table `reports` */

DROP TABLE IF EXISTS `reports`;

CREATE TABLE `reports` (
  `rid` int(11) NOT NULL AUTO_INCREMENT,
  `user_lid` int(11) DEFAULT NULL,
  `upload_id` int(11) DEFAULT NULL,
  `reporting_user` int(11) DEFAULT NULL,
  `date` varchar(15) DEFAULT NULL,
  `time` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`rid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `reports` */

/*Table structure for table `upload_files` */

DROP TABLE IF EXISTS `upload_files`;

CREATE TABLE `upload_files` (
  `fid` int(15) NOT NULL AUTO_INCREMENT,
  `uid` varchar(15) DEFAULT NULL,
  `filename` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`fid`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

/*Data for the table `upload_files` */

insert  into `upload_files`(`fid`,`uid`,`filename`) values 
(9,'6','zayan.shamz6-1.jpg'),
(12,'9','zayan.shamz9-1.jpg'),
(13,'9','zayan.shamz9-2.jpg'),
(14,'9','zayan.shamz9-3.jpg');

/*Table structure for table `uploads` */

DROP TABLE IF EXISTS `uploads`;

CREATE TABLE `uploads` (
  `upload_id` int(15) NOT NULL AUTO_INCREMENT,
  `user_lid` int(15) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `caption` varchar(366) DEFAULT NULL,
  `date` varchar(15) DEFAULT NULL,
  `time` varchar(15) DEFAULT NULL,
  `count` int(15) DEFAULT NULL,
  `fname` varchar(100) DEFAULT NULL,
  `ext` varchar(15) DEFAULT NULL,
  `comment` varchar(15) DEFAULT NULL,
  `like` int(15) DEFAULT NULL,
  PRIMARY KEY (`upload_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;

/*Data for the table `uploads` */

insert  into `uploads`(`upload_id`,`user_lid`,`type`,`caption`,`date`,`time`,`count`,`fname`,`ext`,`comment`,`like`) values 
(6,2,'photo','daaaaamn','2023-03-01','17:03:18',1,'zayan.shamz6','.jpg','no',0),
(9,2,'photo','dvruk','2023-03-22','02:13:29',3,'zayan.shamz9','.jpg','yes',1);

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `uid` int(15) NOT NULL AUTO_INCREMENT,
  `lid` int(15) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `dob` varchar(50) DEFAULT NULL,
  `gender` varchar(50) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `photo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

/*Data for the table `users` */

insert  into `users`(`uid`,`lid`,`name`,`dob`,`gender`,`country`,`email`,`phone`,`photo`) values 
(1,2,'Zayan Shamsudheen','2001-08-13','male','IN','zaynshamz0202@gmail.com','8129777489','zayan.shamz-pfp.jpg'),
(3,4,'Dadul Rishan','2001-10-26','female','IN','dadulrishan@gmail.com','8765897787','dada-pfp.jpeg'),
(5,6,'sithara ','2000-09-19','female','IN','sith@gmail.com','8592002134','sith-pfp.jpeg'),
(6,7,'sith ','2000-09-19','female','AT','sith','6586','nopfp.jpg');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
