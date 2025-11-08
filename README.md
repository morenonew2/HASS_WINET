# WINET-HA - [Stufasmart](http://stufasmart.it/) -
Package e view per i prodotti WINET (stufa da remoto)\
NEWS: AGGIUNTO PKG PER GESTIONE CON API CLOUD (SOLO WINET stufa da remoto)

## Installazione prerequisiti:

-	[HACS](https://www.hacs.xyz/)
  
I pkg seguenti vanno installati tramite HACS

  **INTEGRAZIONI** seguire istruzioni e poi riavviare HA
-	Browser_mod 2
-	Scheduler
  
  **Grafica Interfaccia** dopo installazione aggiornare solo cache browser con CTRL-F5

-	Card-mod
-	Layout-card
- Paper buttons row
- Hui-element
-	Scheduler-card
-	template-entity-row


### Configurazione

Il file configuration.yaml si trova nella cartella di configurazione di Homeassistant

che, in una tipica installazione standard, si trova in:

**˂config˃ = /home/homeassistant/.homeassistant/ (p.es.  installazione tipica su Raspberry)**

****ATTENZIONE! L'INSTALLAZIONE FA FATTA A PARTIRE DALLA CARTELLA DOVE SI TROVA IL FILE CONFIGURATION.YAML****

Aggiungere le seguenti righe al proprio configuration.yaml:

```
homeassistant:
  packages: !include_dir_named packages

lovelace:
  mode: storage
  dashboards:
    lovelace-winet:
      mode: yaml
      title: WINET
      icon: mdi:fire
      show_in_sidebar: true
      filename: winet_dashboard.yaml

```
 


##### Nella cartella ˂config˃ creare  file 
winet_dashboard.yaml:
```
title: WINET
views:
  - !include lovelace/winet_view.yaml
```


### Lovelace
Nella cartella lovelace  (crearla in ˂config˃se non esiste)

Copiare file winet_view.yaml

### Package

Nella cartella packages (crearla in ˂config˃se non esiste)

Copiare file winet_pkg.yaml

### Immagini
Copiare in ˂config˃

la cartella www/Pictures/
 
### Risorse
Impostazioni > Plance > Risorse

Aggiungere 

**URL:** https://fonts.googleapis.com/css?family=Oswald

**Tipo risorsa:** foglio di stile

### Setup

Una volta creata la card impostare l'indirizzo IP della scheda

### Supporta il mio lavoro

[![paypal](https://www.paypalobjects.com/it_IT/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate/?business=mletardi@gmail.com&item_number=Importo+suggerito:+€+2.00+EUR&currency_code=EUR)


![Image alt text](paypal.svg)

![Setup](/www/Pictures/SetupIPWinet.png?raw=true "Setup")

### ScreenShot

![Stufa](/www/Pictures/card.png?raw=true "Card")

![Stufa](/www/Pictures/stove_on.png?raw=true "Status ACCESO")

![Stufa](/www/Pictures/stove_alarm.png?raw=true "Status ALARM")

![Stufa](/www/Pictures/stove_unmanaged.png?raw=true "Status UNMANAGED")

![Stufa alarm](/www/Pictures/stove_unknown.png?raw=true "Status UNKNOWN")

![Stufa](/www/Pictures/stove_final.png?raw=true "Status PULIZIA FINALE")
