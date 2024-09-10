import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import video from "./assets/background.mp4";

function PreMatch() {
    return(
        <>
                <div className='flex flex-col h-screen justify-center items-center'>
                <video autoPlay muted loop className='fixed top-0 left-0 w-full h-full object-cover z-[-2]' > <source src={video} type='video/mp4' /> </video>
                <h1 className='text-5xl font-extrabold' style={{ color: 'white' }}>
                    Try our models with !!!
                </h1>

                    <div className='flex flex-row gap-10 p-10 justify-center items-center'>
                        <Link to="/player-prematch-analysis" className='hover:-translate-y-1 duration-200 ease-in-out 
            text-xl hover:bg-green-400 bg-green-500 px-5 py-3 rounded-xl text-white font-semibold'>
                            Players Analysis
                        </Link >
                        <p className='text-xl'>or</p>
                    <Link to="/team-prematch-analysis" className='hover:-translate-y-1 duration-200 ease-in-out
            text-xl hover:bg-green-500 bg-green-600 px-5 py-3 rounded-xl 
            text-white font-semibold '>
                            Teams Analysis
                        </Link>
                    </div>
                </div>
        </>
    );
}

export default PreMatch;
