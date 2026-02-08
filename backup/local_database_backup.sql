-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: traffic_prediction
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `api_logs`
--

DROP TABLE IF EXISTS `api_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `api_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `endpoint` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API端点',
  `method` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'HTTP方法',
  `request_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '请求IP',
  `request_params` text COLLATE utf8mb4_unicode_ci COMMENT '请求参数（JSON）',
  `response_status` int DEFAULT NULL COMMENT '响应状态码',
  `response_time_ms` int DEFAULT NULL COMMENT '响应时间（毫秒）',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '错误信息（如有）',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_api_logs_response_status` (`response_status`),
  KEY `ix_api_logs_endpoint` (`endpoint`),
  KEY `ix_api_logs_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api_logs`
--

LOCK TABLES `api_logs` WRITE;
/*!40000 ALTER TABLE `api_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `api_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `city_predictions`
--

DROP TABLE IF EXISTS `city_predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `city_predictions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL COMMENT '111',
  `city` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prediction_date` date NOT NULL,
  `time_range` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `weather` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `district` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `other` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flow_per_hour` int NOT NULL,
  `avg_speed` float NOT NULL,
  `congestion_index` float NOT NULL,
  `severity` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `confidence` float NOT NULL,
  `index_score` float NOT NULL,
  `extra_payload` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_city_predictions_prediction_date` (`prediction_date`),
  KEY `ix_city_predictions_city` (`city`),
  KEY `ix_city_predictions_created_at` (`created_at`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `city_predictions`
--

LOCK TABLES `city_predictions` WRITE;
/*!40000 ALTER TABLE `city_predictions` DISABLE KEYS */;
INSERT INTO `city_predictions` VALUES (1,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 14:45:50'),(2,2,'青岛','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',7306,53.7,0.51,'一般',0.84,48.71,'{\"city\": \"青岛\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 14:46:33'),(3,2,'厦门','2025-11-06','晚高峰（16:00-19:00）','多云','主城区','',7998,50,0.47,'一般',0.85,53.32,'{\"city\": \"厦门\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"多云\", \"district\": \"主城区\", \"other\": \"\"}','2025-11-06 15:54:32'),(4,2,'郑州','2025-11-06','晚高峰（16:00-19:00）','雾霾','其他','',7317,54.3,0.5,'一般',0.88,48.78,'{\"city\": \"郑州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"雾霾\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 15:55:10'),(5,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 15:57:05'),(6,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',500,2.5,0.54,'畅通',0.85,3.33,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\", \"model_type\": \"LSTM\", \"data_source\": \"DeepLearning_Model\"}','2025-11-06 16:39:51'),(7,2,'郑州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',500,2.4,0.55,'畅通',0.85,3.33,'{\"city\": \"郑州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\", \"model_type\": \"LSTM\", \"data_source\": \"DeepLearning_Model\"}','2025-11-06 16:40:02'),(8,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',500,2.5,0.54,'畅通',0.85,3.33,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\", \"model_type\": \"LSTM\", \"data_source\": \"DeepLearning_Model\"}','2025-11-06 16:40:13'),(9,2,'西安','2025-11-06','夜间（22:00-24:00）','大雨','商务区','',500,1.9,0.6,'正常',0.85,3.33,'{\"city\": \"西安\", \"date\": \"2025-11-06\", \"time_range\": \"夜间（22:00-24:00）\", \"weather\": \"大雨\", \"district\": \"商务区\", \"other\": \"\", \"model_type\": \"LSTM\", \"data_source\": \"DeepLearning_Model\"}','2025-11-06 16:41:33'),(10,2,'成都','2025-11-06','午间时段（12:00-14:00）','暴雪','商务区','',500,2.2,0.57,'正常',0.85,3.33,'{\"city\": \"成都\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"暴雪\", \"district\": \"商务区\", \"other\": \"\", \"model_type\": \"LSTM\", \"data_source\": \"DeepLearning_Model\"}','2025-11-06 16:43:42'),(11,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 16:45:35'),(12,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 17:02:07'),(13,2,'西安','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',7387,49.1,0.5,'一般',0.84,49.25,'{\"city\": \"西安\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 17:03:48'),(14,2,'重庆','2025-11-06','晚高峰（16:00-19:00）','多云','商务区','',10015,41.4,0.7,'拥堵',0.82,66.77,'{\"city\": \"重庆\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"多云\", \"district\": \"商务区\", \"other\": \"\"}','2025-11-06 17:12:47'),(15,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','暴雪','其他','',7381,52,0.51,'一般',0.9,49.21,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"暴雪\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 19:29:41'),(16,2,'青岛','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',7306,53.7,0.51,'一般',0.84,48.71,'{\"city\": \"青岛\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 19:30:45'),(17,2,'佛山','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',6304,57.2,0.49,'一般',0.84,42.03,'{\"city\": \"佛山\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 19:31:11'),(18,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 20:17:50'),(19,2,'杭州','2025-11-06','晚高峰（16:00-19:00）','大雨','其他','',8051,49.6,0.45,'一般',0.83,53.67,'{\"city\": \"杭州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"\"}','2025-11-06 21:14:41'),(20,2,'广州','2025-11-06','午间时段（12:00-14:00）','多云','高校区','节假日',7682,50.4,0.51,'一般',0.84,51.21,'{\"city\": \"广州\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"多云\", \"district\": \"高校区\", \"other\": \"节假日\"}','2025-11-06 21:18:18'),(21,2,'武汉','2025-11-06','午间时段（12:00-14:00）','暴雪','住宅区','无',5184,55.4,0.23,'畅通',0.91,34.56,'{\"city\": \"武汉\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"暴雪\", \"district\": \"住宅区\", \"other\": \"无\"}','2025-11-06 21:23:00'),(22,2,'重庆','2025-11-06','早高峰（07:00-09:00）','晴','景区','无',9083,48,0.68,'拥堵',0.84,60.55,'{\"city\": \"重庆\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"晴\", \"district\": \"景区\", \"other\": \"无\"}','2025-11-06 21:33:42'),(23,2,'上海','2025-11-06','早高峰（07:00-09:00）','小雨','商务区','无',11243,44.8,0.85,'严重',0.87,74.95,'{\"city\": \"上海\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"小雨\", \"district\": \"商务区\", \"other\": \"无\"}','2025-11-06 22:50:50'),(24,2,'成都','2025-11-06','午间时段（12:00-14:00）','暴雪','其他','无',5583,54.7,0.23,'畅通',0.85,37.22,'{\"city\": \"成都\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"暴雪\", \"district\": \"其他\", \"other\": \"无\"}','2025-11-06 22:51:19'),(25,2,'重庆','2025-11-06','早高峰（07:00-09:00）','暴雪','工业区','无',6541,54.5,0.51,'一般',0.85,43.61,'{\"city\": \"重庆\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"暴雪\", \"district\": \"工业区\", \"other\": \"无\"}','2025-11-06 23:06:52'),(26,2,'上海','2025-11-06','早高峰（07:00-09:00）','沙尘暴','住宅区','无',8012,51.2,0.48,'一般',0.87,53.41,'{\"city\": \"上海\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"沙尘暴\", \"district\": \"住宅区\", \"other\": \"无\"}','2025-11-06 23:10:48'),(27,2,'上海','2025-11-06','午间时段（12:00-14:00）','多云','高校区','无',8494,49.2,0.51,'一般',0.89,56.63,'{\"city\": \"上海\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"多云\", \"district\": \"高校区\", \"other\": \"无\"}','2025-11-06 23:23:07'),(28,2,'广州','2025-11-06','早高峰（07:00-09:00）','大雨','高校区','无',8510,51.5,0.68,'拥堵',0.87,56.73,'{\"city\": \"广州\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"大雨\", \"district\": \"高校区\", \"other\": \"无\"}','2025-11-06 23:27:49'),(29,2,'广州','2025-11-06','晚高峰（16:00-19:00）','晴','主城区','无',10964,40.5,0.69,'拥堵',0.89,73.09,'{\"city\": \"广州\", \"date\": \"2025-11-06\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"晴\", \"district\": \"主城区\", \"other\": \"无\"}','2025-11-06 23:32:08'),(30,2,'天津','2025-11-06','午间时段（12:00-14:00）','暴雪','高校区','无',4618,57.5,0.18,'畅通',0.87,30.79,'{\"city\": \"天津\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"暴雪\", \"district\": \"高校区\", \"other\": \"无\"}','2025-11-06 23:33:24'),(31,2,'重庆','2025-11-06','早高峰（07:00-09:00）','雾霾','景区','无',8017,51.9,0.45,'一般',0.91,53.45,'{\"city\": \"重庆\", \"date\": \"2025-11-06\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"雾霾\", \"district\": \"景区\", \"other\": \"无\"}','2025-11-06 23:43:11'),(32,2,'天津','2025-11-06','午间时段（12:00-14:00）','暴雪','住宅区','无',4886,53.9,0.22,'畅通',0.85,32.57,'{\"city\": \"天津\", \"date\": \"2025-11-06\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"暴雪\", \"district\": \"住宅区\", \"other\": \"无\"}','2025-11-06 23:47:39'),(33,2,'成都','2025-11-07','晚高峰（16:00-19:00）','暴雪','住宅区','无',6456,49.6,0.45,'一般',0.89,43.04,'{\"city\": \"成都\", \"date\": \"2025-11-07\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"暴雪\", \"district\": \"住宅区\", \"other\": \"无\"}','2025-11-07 00:43:32'),(34,2,'天津','2025-11-07','早高峰（07:00-09:00）','大雨','高校区','无',6540,54.3,0.49,'一般',0.9,43.6,'{\"city\": \"天津\", \"date\": \"2025-11-07\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"大雨\", \"district\": \"高校区\", \"other\": \"无\"}','2025-11-07 00:55:04'),(35,2,'武汉','2025-11-07','午间时段（12:00-14:00）','小雨','其他','无',7364,47.5,0.5,'一般',0.85,49.09,'{\"city\": \"武汉\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"小雨\", \"district\": \"其他\", \"other\": \"无\"}','2025-11-07 00:55:44'),(36,2,'西安','2025-11-07','早高峰（07:00-09:00）','沙尘暴','工业区','无',6169,57.2,0.45,'一般',0.89,41.13,'{\"city\": \"西安\", \"date\": \"2025-11-07\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"沙尘暴\", \"district\": \"工业区\", \"other\": \"无\"}','2025-11-07 00:56:20'),(37,2,'重庆','2025-11-07','午间时段（12:00-14:00）','大雨','住宅区','演唱会',5347,57.7,0.25,'畅通',0.83,35.65,'{\"city\": \"重庆\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"大雨\", \"district\": \"住宅区\", \"other\": \"演唱会\"}','2025-11-07 01:09:15'),(38,2,'成都','2025-11-07','午间时段（12:00-14:00）','大雨','其他','无',6701,53.2,0.46,'一般',0.91,44.67,'{\"city\": \"成都\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"大雨\", \"district\": \"其他\", \"other\": \"无\"}','2025-11-07 01:12:29'),(39,2,'重庆','2025-11-07','早高峰（07:00-09:00）','暴雪','其他','无',6595,50.1,0.5,'一般',0.83,43.97,'{\"city\": \"重庆\", \"date\": \"2025-11-07\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"暴雪\", \"district\": \"其他\", \"other\": \"无\"}','2025-11-07 01:21:48'),(40,2,'重庆','2025-11-07','午间时段（12:00-14:00）','晴','工业区','无',7532,53.8,0.46,'一般',0.87,50.21,'{\"city\": \"重庆\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"晴\", \"district\": \"工业区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTQ0MjY5fQ.9QTTbsv6PtUw09U1rxdsw1GOIg_Dg4xZNkWJPH6A4B0\"}','2025-11-07 03:45:36'),(41,2,'天津','2025-11-07','晚高峰（16:00-19:00）','暴雪','景区','无',6988,52,0.46,'一般',0.9,46.59,'{\"city\": \"天津\", \"date\": \"2025-11-07\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"暴雪\", \"district\": \"景区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTQ0MjY5fQ.9QTTbsv6PtUw09U1rxdsw1GOIg_Dg4xZNkWJPH6A4B0\"}','2025-11-07 12:17:45'),(42,2,'广州','2025-11-07','晚高峰（16:00-19:00）','多云','商务区','无',11523,39.2,0.87,'严重',0.88,76.82,'{\"city\": \"广州\", \"date\": \"2025-11-07\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"多云\", \"district\": \"商务区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTQ0MjY5fQ.9QTTbsv6PtUw09U1rxdsw1GOIg_Dg4xZNkWJPH6A4B0\"}','2025-11-07 12:38:15'),(43,2,'成都','2025-11-07','早高峰（07:00-09:00）','沙尘暴','景区','无',7923,45.5,0.44,'一般',0.92,52.82,'{\"city\": \"成都\", \"date\": \"2025-11-07\", \"time_range\": \"早高峰（07:00-09:00）\", \"weather\": \"沙尘暴\", \"district\": \"景区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTQ0MjY5fQ.9QTTbsv6PtUw09U1rxdsw1GOIg_Dg4xZNkWJPH6A4B0\"}','2025-11-07 12:38:53'),(44,2,'苏州','2025-11-07','晚高峰（16:00-19:00）','大雨','高校区','无',7166,51,0.48,'一般',0.85,47.77,'{\"city\": \"苏州\", \"date\": \"2025-11-07\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"大雨\", \"district\": \"高校区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTQ0MjY5fQ.9QTTbsv6PtUw09U1rxdsw1GOIg_Dg4xZNkWJPH6A4B0\"}','2025-11-07 12:43:28'),(45,2,'西安','2025-11-07','午间时段（12:00-14:00）','大雨','住宅区','施工',5252,52.4,0.18,'畅通',0.89,35.01,'{\"city\": \"西安\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"大雨\", \"district\": \"住宅区\", \"other\": \"施工\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNTc3MzU5fQ.-v2AUOEH5V8_onkMLNOKwSkU9iTlLfsdWr1alcFfK_k\"}','2025-11-07 15:36:50'),(46,2,'成都','2025-11-07','午间时段（12:00-14:00）','雾霾','工业区','无',6873,49.8,0.45,'一般',0.85,45.82,'{\"city\": \"成都\", \"date\": \"2025-11-07\", \"time_range\": \"午间时段（12:00-14:00）\", \"weather\": \"雾霾\", \"district\": \"工业区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNjA2MTMxfQ.rMB9t3o1_tGG9HrDblbsw_FjISccKleyUKF9yrHulZk\"}','2025-11-07 20:49:18'),(47,2,'成都','2025-11-07','晚高峰（16:00-19:00）','暴雪','住宅区','无',6456,49.6,0.45,'一般',0.89,43.04,'{\"city\": \"成都\", \"date\": \"2025-11-07\", \"time_range\": \"晚高峰（16:00-19:00）\", \"weather\": \"暴雪\", \"district\": \"住宅区\", \"other\": \"无\", \"token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjExMSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzYyNjA2MTMxfQ.rMB9t3o1_tGG9HrDblbsw_FjISccKleyUKF9yrHulZk\"}','2025-11-07 20:55:54');
/*!40000 ALTER TABLE `city_predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `model_performance`
--

DROP TABLE IF EXISTS `model_performance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model_performance` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `model_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模型名称',
  `model_version` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模型版本',
  `test_dataset` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '测试数据集',
  `metric_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '指标名称',
  `metric_value` float NOT NULL COMMENT '指标值',
  `evaluation_time` datetime NOT NULL COMMENT '评估时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_model_performance_evaluation_time` (`evaluation_time`),
  KEY `ix_model_performance_model_name` (`model_name`),
  KEY `ix_model_performance_metric_name` (`metric_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model_performance`
--

LOCK TABLES `model_performance` WRITE;
/*!40000 ALTER TABLE `model_performance` DISABLE KEYS */;
/*!40000 ALTER TABLE `model_performance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `predictions`
--

DROP TABLE IF EXISTS `predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictions` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `sensor_id` int NOT NULL COMMENT '传感器ID',
  `prediction_time` datetime NOT NULL COMMENT '预测时间',
  `target_time` datetime NOT NULL COMMENT '目标时间',
  `flow_prediction` float DEFAULT NULL COMMENT '流量预测值',
  `flow_actual` float DEFAULT NULL COMMENT '实际流量值',
  `density_prediction` float DEFAULT NULL COMMENT '密度预测值',
  `density_actual` float DEFAULT NULL COMMENT '实际密度值',
  `congestion_prediction` enum('畅通','正常','拥堵','严重拥堵') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '拥堵状态预测',
  `congestion_actual` enum('畅通','正常','拥堵','严重拥堵') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '实际拥堵状态',
  `confidence` float DEFAULT NULL COMMENT '预测置信度',
  `model_version` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '使用的模型版本',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_predictions_sensor_id` (`sensor_id`),
  KEY `ix_predictions_model_version` (`model_version`),
  KEY `ix_predictions_prediction_time` (`prediction_time`),
  KEY `ix_predictions_target_time` (`target_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `predictions`
--

LOCK TABLES `predictions` WRITE;
/*!40000 ALTER TABLE `predictions` DISABLE KEYS */;
/*!40000 ALTER TABLE `predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_config`
--

DROP TABLE IF EXISTS `system_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_config` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `config_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` text COLLATE utf8mb4_unicode_ci COMMENT '配置值',
  `config_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置类型',
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置说明',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_system_config_config_key` (`config_key`),
  KEY `ix_system_config_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_config`
--

LOCK TABLES `system_config` WRITE;
/*!40000 ALTER TABLE `system_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `system_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_records`
--

DROP TABLE IF EXISTS `training_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_records` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `model_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模型名称（LSTM/GRU）',
  `model_version` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模型版本号',
  `start_time` datetime NOT NULL COMMENT '训练开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '训练结束时间',
  `duration_seconds` int DEFAULT NULL COMMENT '训练时长（秒）',
  `epochs` int DEFAULT NULL COMMENT '训练轮数',
  `batch_size` int DEFAULT NULL COMMENT '批大小',
  `learning_rate` float DEFAULT NULL COMMENT '学习率',
  `optimizer` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '优化器',
  `train_loss` float DEFAULT NULL COMMENT '最终训练损失',
  `val_loss` float DEFAULT NULL COMMENT '最终验证损失',
  `best_epoch` int DEFAULT NULL COMMENT '最佳模型对应的epoch',
  `mae` float DEFAULT NULL COMMENT 'Mean Absolute Error',
  `rmse` float DEFAULT NULL COMMENT 'Root Mean Square Error',
  `mape` float DEFAULT NULL COMMENT 'Mean Absolute Percentage Error',
  `accuracy` float DEFAULT NULL COMMENT '分类准确率',
  `model_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模型文件路径',
  `config_json` text COLLATE utf8mb4_unicode_ci COMMENT '完整配置（JSON格式）',
  `status` enum('running','completed','failed','stopped') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '训练状态',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_training_records_model_version` (`model_version`),
  KEY `ix_training_records_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_records`
--

LOCK TABLES `training_records` WRITE;
/*!40000 ALTER TABLE `training_records` DISABLE KEYS */;
INSERT INTO `training_records` VALUES (1,'LSTM','lstm_v20251106_202948','2025-11-06 20:29:48','2025-11-06 20:33:27',218,50,64,0.001,'Adam',0.00142957,0.000468811,16,NULL,NULL,NULL,NULL,'data\\models\\best\\lstm_best.pth','{\"learning_rate\": 0.001, \"optimizer\": \"Adam\", \"weight_decay\": 1e-05, \"batch_size\": 64, \"early_stopping\": {\"patience\": 10}, \"scheduler\": {\"type\": \"ReduceLROnPlateau\", \"patience\": 5}}','completed',NULL,'2025-11-06 12:29:48','2025-11-06 12:33:27'),(2,'GRU','gru_v20251106_204647','2025-11-06 20:46:48','2025-11-06 20:52:49',361,50,64,0.001,'Adam',0.00130072,0.000368639,19,NULL,NULL,NULL,NULL,'data\\models\\best\\gru_best.pth','{\"learning_rate\": 0.001, \"optimizer\": \"Adam\", \"weight_decay\": 1e-05, \"batch_size\": 64, \"early_stopping\": {\"patience\": 10}, \"scheduler\": {\"type\": \"ReduceLROnPlateau\", \"patience\": 5}}','completed',NULL,'2025-11-06 12:46:47','2025-11-06 12:52:49');
/*!40000 ALTER TABLE `training_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `nickname` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '昵称',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'user' COMMENT '角色：admin/user',
  `status` tinyint DEFAULT '1' COMMENT '状态：1-正常，0-禁用',
  `last_login_time` datetime DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最后登录IP',
  `login_count` int DEFAULT '0' COMMENT '登录次数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `prediction_count` int DEFAULT '0' COMMENT '预测次数',
  `model_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'lstm' COMMENT '选择的模型类型：lstm/gru',
  `weather_weight` float DEFAULT '0.25' COMMENT '天气因素权重',
  `time_weight` float DEFAULT '0.25' COMMENT '时间段因素权重',
  `district_weight` float DEFAULT '0.25' COMMENT '城市功能区因素权重',
  `other_weight` float DEFAULT '0.25' COMMENT '其他因素权重',
  `use_gpu` tinyint(1) DEFAULT '0' COMMENT '是否使用GPU加速',
  `multi_predict` tinyint(1) DEFAULT '0' COMMENT '是否多次预测',
  `receive_email` tinyint(1) DEFAULT '1' COMMENT '是否接收邮件通知',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@traffic.com','$2b$12$8cGK2oVISHD0kGZwNkLa3.pkxCT4yzk.nUX/w/mfUVpWFF0tLSU7W','系统管理员',NULL,'admin',1,NULL,NULL,0,'2025-11-06 14:36:49','2025-11-06 14:36:49',0,'lstm',0.25,0.25,0.25,0.25,0,0,1),(2,'111','2192632011@qq.com','$2b$12$flQQwQcPDRukc1cq4xD2TeYliaTHYamqMvOPsWyEjhPMo8ZOoh4Ou','jaryl','/static/avatars/2_e4f74aad.png','user',1,'2025-11-07 20:59:22','127.0.0.1',32,'2025-11-06 14:44:50','2025-11-07 20:59:22',47,'lstm',0.7,0.3,0,0,1,1,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-07 22:44:40
