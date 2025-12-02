-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         10.4.28-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para nutritrack
CREATE DATABASE IF NOT EXISTS `nutritrack` /*!40100 DEFAULT CHARACTER SET utf32 COLLATE utf32_spanish_ci */;
USE `nutritrack`;

-- Volcando estructura para tabla nutritrack.alimentos_registrados
CREATE TABLE IF NOT EXISTS `alimentos_registrados` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) DEFAULT NULL,
  `alimento` varchar(255) NOT NULL,
  `cantidad` decimal(8,2) NOT NULL,
  `unidad` varchar(50) NOT NULL,
  `calorias` decimal(8,2) NOT NULL,
  `proteinas` decimal(8,2) DEFAULT NULL,
  `carbohidratos` decimal(8,2) DEFAULT NULL,
  `grasas` decimal(8,2) DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `alimentos_registrados_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf32 COLLATE=utf32_spanish_ci;

-- Volcando datos para la tabla nutritrack.alimentos_registrados: ~0 rows (aproximadamente)
DELETE FROM `alimentos_registrados`;

-- Volcando estructura para tabla nutritrack.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` enum('Mujer','Hombre','Personalizado') DEFAULT NULL,
  `peso` decimal(5,2) DEFAULT NULL,
  `altura` decimal(5,2) DEFAULT NULL,
  `actividad_fisica` varchar(50) DEFAULT NULL,
  `dieta_especifica` varchar(50) DEFAULT NULL,
  `experiencia_cocina` varchar(50) DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf32 COLLATE=utf32_spanish_ci;

-- Volcando datos para la tabla nutritrack.usuarios: ~1 rows (aproximadamente)
DELETE FROM `usuarios`;
INSERT INTO `usuarios` (`id`, `nombre`, `apellido`, `email`, `password`, `fecha_nacimiento`, `genero`, `peso`, `altura`, `actividad_fisica`, `dieta_especifica`, `experiencia_cocina`, `fecha_registro`) VALUES
	(1, 'Omar ', 'ort ', 'omar@correo.com', 'scrypt:32768:8:1$oavB2qYtAgUcV75n$5b7ddf04ae1fa66e130a256a26033e9896c376e10e3d05058cdbf8e2afb20d68edde99660a02856d4bbad6faa3d981b883c8521443f16bd196a7934eed02e43b', '2008-09-14', 'Hombre', 61.00, 170.00, 'sedentario', '', 'principiante', '2025-12-02 16:40:16');

-- Volcando estructura para tabla nutritrack.usuario_alergias
CREATE TABLE IF NOT EXISTS `usuario_alergias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) DEFAULT NULL,
  `alergia` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `usuario_alergias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf32 COLLATE=utf32_spanish_ci;

-- Volcando datos para la tabla nutritrack.usuario_alergias: ~1 rows (aproximadamente)
DELETE FROM `usuario_alergias`;
INSERT INTO `usuario_alergias` (`id`, `usuario_id`, `alergia`) VALUES
	(1, 1, 'niguno');

-- Volcando estructura para tabla nutritrack.usuario_intolerancias
CREATE TABLE IF NOT EXISTS `usuario_intolerancias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) DEFAULT NULL,
  `intolerancia` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `usuario_intolerancias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf32 COLLATE=utf32_spanish_ci;

-- Volcando datos para la tabla nutritrack.usuario_intolerancias: ~1 rows (aproximadamente)
DELETE FROM `usuario_intolerancias`;
INSERT INTO `usuario_intolerancias` (`id`, `usuario_id`, `intolerancia`) VALUES
	(1, 1, 'ninguno');

-- Volcando estructura para tabla nutritrack.usuario_objetivos
CREATE TABLE IF NOT EXISTS `usuario_objetivos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) DEFAULT NULL,
  `objetivo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `usuario_objetivos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf32 COLLATE=utf32_spanish_ci;

-- Volcando datos para la tabla nutritrack.usuario_objetivos: ~1 rows (aproximadamente)
DELETE FROM `usuario_objetivos`;
INSERT INTO `usuario_objetivos` (`id`, `usuario_id`, `objetivo`) VALUES
	(1, 1, 'mantener_peso');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
