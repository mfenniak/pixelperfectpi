# Subscribe & Observe all MQTT Traffic

```
mosquitto_sub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD -t "#" -v
```

# Turn clock on & off

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t homeassistant/pixelperfectpi/$(hostname)/cmd -m ON
```

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t homeassistant/pixelperfectpi/$(hostname)/cmd -m OFF
```


# Send test media player status

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t "homeassistant/output/media/family_room_tv" \
    --retain \
    -m "{ \"state\": \"playing\", \"position\": 60, \"duration\": 1712, \"updated_at\": \"$(date +"%Y-%m-%d %H:%M:%S.%6N%:z")\" }"
```

# Send test location

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t "homeassistant/output/location/mathieu" \
    --retain \
    -m '{ "latitude": 51.1364423, "longitude": -114.3045712, "accuracy": 100 }'
```

# Send test door state

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t "homeassistant/output/door/garage_door" \
    --retain \
    -m "{ \"timestamp\": \"$(date +"%Y-%m-%d %H:%M:%S.%6N%:z")\", \"state\": \"open\" }"
```

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t "homeassistant/output/door/garage_door" \
    --retain \
    -m "{ \"timestamp\": \"$(date +"%Y-%m-%d %H:%M:%S.%6N%:z")\", \"state\": \"closed\" }"
```

## Left open a long time

```
mosquitto_pub -h $MQTT_HOST -u $MQTT_USERNAME -P $MQTT_PASSWORD \
    -t "homeassistant/output/door/garage_door" \
    --retain \
    -m "{ \"timestamp\": \"2020-01-01 01:01:01.000-00:00\", \"state\": \"open\" }"
```
