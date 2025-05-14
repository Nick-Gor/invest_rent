CREATE TABLE `investrent`.`metersverkh` (
  `num` INT NOT NULL,
  `number_v` VARCHAR(20) NOT NULL,
  `coefficient` INT NOT NULL,
  `place` VARCHAR(80) NOT NULL,
  `tenant` VARCHAR(45) NOT NULL,
  `enviroment` VARCHAR(12) NOT NULL,
  `coordinates` VARCHAR(20) NULL,
  PRIMARY KEY (`number`));