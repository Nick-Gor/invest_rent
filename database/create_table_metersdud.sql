CREATE TABLE IF NOT EXISTS `nbg$investrent`.`metersdud` (
  `num` INT NOT NULL,
  `number` VARCHAR(20) NOT NULL,
  `coefficient` VARCHAR(2) NOT NULL,
  `place` VARCHAR(80) NOT NULL,
  `tenant` VARCHAR(45) NOT NULL,
  `enviroment` VARCHAR(12) NOT NULL,
  `coordinats` VARCHAR(20) NULL,
  PRIMARY KEY (`number`))
ENGINE = InnoDB;