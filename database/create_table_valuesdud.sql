CREATE TABLE IF NOT EXISTS `nbg$investrent`.`valuesdud` (
  `number` VARCHAR(16) NOT NULL,
  `enviroment` VARCHAR(11) NOT NULL,
  `month` VARCHAR(8) NOT NULL,
  `date` VARCHAR(10),
  `debet` INT NOT NULL,
  `value` INT NOT NULL,
  `coordinats` VARCHAR(20) NULL,
  INDEX `number_idx` (`number` ASC) VISIBLE,
  CONSTRAINT `number`
    FOREIGN KEY (`number`)
    REFERENCES `nbg$investrent`.`metersdud` (`number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

ALTER TABLE `nbg$investrent`.`valuesdud` 
  ADD COLUMN `num` INT NOT NULL AUTO_INCREMENT FIRST,
  ADD PRIMARY KEY (`num`);