CREATE TABLE `nbg$investrent`.`valuesverkh` (
  `num` INT NOT NULL AUTO_INCREMENT,
  `number_v` VARCHAR(16) NOT NULL,
  `enviroment` VARCHAR(11) NOT NULL,
  `year` INT NOT NULL,
  `month` VARCHAR(8) NOT NULL,
  `date` VARCHAR(10) NOT NULL,
  `debit` INT NOT NULL,
  `value` INT NOT NULL,
  `coordinates` VARCHAR(20) NULL,
  PRIMARY KEY (`num`),
  INDEX `number_idx` (`number_v` ASC) VISIBLE,
  CONSTRAINT `number_v`
    FOREIGN KEY (`number_v`)
    REFERENCES `nbg$investrent`.`metersverkh` (`number_v`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE);