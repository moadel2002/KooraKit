// src/UploadVideo.js
import React, { useState } from 'react';
import axios from 'axios';

const UploadVideo = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [data, setData] = useState(null);
  
  const [team1_data, setTeam1Data] = useState(null);
  const [team2_data, setTeam2Data] = useState(null);
  const [selectedPlayer1, setSelectedPlayer1] = useState(null);
  const [selectedPlayer2, setSelectedPlayer2] = useState(null);

  const handlePlayer1Change = (event) => {
    const playerId = event.target.value;
    setSelectedPlayer1(playerId);
  };

  const handlePlayer2Change = (event) => {
    const playerId = event.target.value;
    setSelectedPlayer2(playerId);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    const fileUrl = URL.createObjectURL(file);
    setPreviewUrl(fileUrl);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('video', selectedFile);

    // const obj = {
    //     1:{
    //         'team':1,
    //         'dist':12,
    //         'speed':13,
    //         'heat':'np_image'
    //     },
    //     2:{
    //         'team':2,
    //         'dist':15,
    //         'speed':20,
    //         'heat':'np_image'
    //     }
    // }

    // const team1 = []
    // const team2 = []

    // for(let id in obj){
    //   obj[id].id = id;
    //   if(obj[id].team == 1) team1.push(obj[id])
    //   else team2.push(obj[id])
    // }
    
    // setTeam1Data(team1)
    // setTeam2Data(team2)


    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      alert('File uploaded successfully');
      const team1 = []
      const team2 = []

      const obj = response.data
      console.log(response.data)
      for(let id in obj){
        obj[id].id = id;
        if(obj[id].teams == 0) team1.push(obj[id])
        else team2.push(obj[id])
      }
      
      setTeam1Data(team1)
      setTeam2Data(team2)
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file');
    }
  };

  return (
    <div className='flex flex-col'>
      <h2 className='self-start text-5xl font-extrabold text-white'>Upload Video</h2>
      <input 
        className='hover:-translate-y-1 duration-200 ease-in-out text-xl hover:bg-green-500 bg-green-600 px-5 py-3 rounded-xl text-white font-semibold my-4'  
        type="file" 
        accept="video/*" 
        onChange={handleFileChange} 
      />
      <button 
        className='hover:-translate-y-1 duration-200 ease-in-out text-xl hover:bg-green-500 bg-green-600 px-5 py-3 rounded-xl text-white font-semibold' 
        onClick={handleUpload}
      >
        Upload
      </button>
  
      <div className="flex justify-between mt-4 w-full">
        {team1_data && (
          <div className="flex flex-col items-end">
            <div className="bg-green-500 rounded-md p-2 inline-block">
              <h1 className="text-white text-lg">Team 1:</h1>
            </div>
            <select
              name="team1_player"
              onChange={handlePlayer1Change}
              className="w-full p-2 mt-4 mb-6 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            >
              <option disabled selected value> -- select an option -- </option>
              {Object.keys(team1_data).map((key) => (
                <option key={team1_data[key].id} value={team1_data[key].id}>
                  Player {team1_data[key].id}
                </option>
              ))}
            </select>
            {selectedPlayer1 && team1_data[selectedPlayer1] && (
              <div className="bg-green-500 border border-green-600 shadow-md rounded-md p-4">
                <p className="text-white text-lg">Distance: {team1_data[selectedPlayer1].distance}</p>
                <p className="text-white text-lg">Speed: {team1_data[selectedPlayer1].speed}</p>
                <img src={`data:image/png;base64,${team1_data[selectedPlayer1].heat}`} alt="Heatmap" className="mt-4 rounded-md" />
              </div>
            )}
          </div>
        )}
  
        {team2_data && (
          <div className="flex flex-col items-start">
            <div className="bg-green-500 rounded-md p-2 inline-block">
              <h1 className="text-white text-lg">Team 2:</h1>
            </div>
            <select
              name="team2_player"
              onChange={handlePlayer2Change}
              className="w-full p-2 mt-4 mb-6 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            >
              <option disabled selected value> -- select an option -- </option>
              {Object.keys(team2_data).map((key) => (
                <option key={team2_data[key].id} value={team2_data[key].id}>
                  Player {team2_data[key].id}
                </option>
              ))}
            </select>
            {selectedPlayer2 && team2_data[selectedPlayer2] && (
              <div className="bg-green-500 border border-green-600 shadow-md rounded-md p-4">
                <p className="text-white text-lg">Distance: {team2_data[selectedPlayer2].distance}</p>
                <p className="text-white text-lg">Speed: {team2_data[selectedPlayer2].speed}</p>
                <img src={`data:image/png;base64,${team2_data[selectedPlayer2].heat}`} alt="Heatmap" className="mt-4 rounded-md" />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
  
};

export default UploadVideo;