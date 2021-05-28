const bip39 = require('bip39');

const Web3API = require('web3');

const web3 = new Web3API(new Web3API.providers.HttpProvider('https://mainnet.infura.io/v3/90abced86fd9411ea27beacdb82e5765'));

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('Enter mnemonic: ', (mnemonic) => {
  rl.question('Enter path: ', (path) => {
    const seed = bip39.mnemonicToSeedSync(mnemonic).toString('hex');
    const spawn = require("child_process").spawn;
    const pythonProcess = spawn('python',["address_from_seed.py", seed]);


    pythonProcess.stdout.on('data', (data) => {
        let data_str = data.toString();
        let x = data_str.split('\r');
        let pk = x[0];
        let addr = x[1].slice(1);
        let account = {
            privateKey: pk,
            address: addr
        };
        let wallet = web3.eth.accounts.wallet.add(account);
        web3.eth.getBalance(addr, function(err, result) {
            if (err) {
                console.log(err)
                } else {
                console.log(`address: ${addr}\nbalance: ${web3.utils.fromWei(result, "ether")} ETH`);
                }
            });
    });

    rl.close();
  });
});


