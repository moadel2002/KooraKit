import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import video from "./assets/background.mp4";

function Home() {

    return (
        <>
            <div className='fixed top-0 left-0 w-full h-full object-cover z-[-1] bg-black bg-opacity-40'></div>
            <video autoPlay muted loop className='fixed top-0 left-0 w-full h-full object-cover z-[-2]' > <source src={video} type='video/mp4' /> </video>
            <div className='flex flex-col h-screen justify-center text-white items-center'>
                <h1 className='text-5xl font-extrabold'>
                    Koora Kit
                </h1>
                <h1 className='text-2xl font-semibold pt-3 text-white'>
                    AI Toolkit for Soccer Analytics
                </h1>
                <div className='flex flex-row gap-10 p-10 justify-center items-center'>
                    <Link to="/prematch" className='hover:-translate-y-1 duration-200 ease-in-out 
            text-xl hover:bg-green-400 bg-green-500 px-5 py-3 rounded-xl text-white font-semibold'>
                        Pre-Game Analysis
                    </Link >
                    <p className='text-xl'>or</p>
                    <Link to="/postmatch" className='hover:-translate-y-1 duration-200 ease-in-out
            text-xl hover:bg-green-500 bg-green-600 px-5 py-3 rounded-xl 
            text-white font-semibold '>
                        Post-Game Analysis
                    </Link>
                </div>
            </div>
        </>
    );

}

export default Home;
