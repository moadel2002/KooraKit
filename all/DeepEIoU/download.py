from SoccerNet.Downloader import SoccerNetDownloader
mySoccerNetDownloader = SoccerNetDownloader(LocalDirectory="/media/samar/HDD1T/Deep-EIoU/tracking")
mySoccerNetDownloader.downloadDataTask(task="tracking-2023", split=["train", "test", "challenge"])