ALTER TABLE `liai_concrete`.`grupo`
ADD COLUMN `id_fisico` VARCHAR(45) NULL AFTER `grupo_nombre`;

ALTER TABLE `liai_concrete`.`grupo`
CHANGE COLUMN `grupo_id` `nodo_id` INT NOT NULL AUTO_INCREMENT ,
CHANGE COLUMN `grupo_nombre` `nombre` VARCHAR(255) NULL DEFAULT NULL , RENAME TO  `liai_concrete`.`nodo` ;

ALTER TABLE `liai_concrete`.`tarjeta`
DROP FOREIGN KEY `tarjeta_ibfk_1`;
ALTER TABLE `liai_concrete`.`tarjeta`
CHANGE COLUMN `grupo_id` `nodo_id` INT NULL DEFAULT NULL ;
ALTER TABLE `liai_concrete`.`tarjeta`
ADD CONSTRAINT `tarjeta_ibfk_1`
  FOREIGN KEY (`nodo_id`)
  REFERENCES `liai_concrete`.`nodo` (`nodo_id`);
