# hacker-kiosk

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run electron:serve
```

### Compiles and minifies for production
```
npm run electron:build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

### Run the backend with
```
export PYTHONPATH=$PWD/../../cyberphyslib
python3 kiosk-backend.py --network-config ../../../base/utils/setupEnv.json
```

## Run the tester with
```
export PYTHONPATH=$PWD/../../cyberphyslib
python3 kiosk-tester.py
```