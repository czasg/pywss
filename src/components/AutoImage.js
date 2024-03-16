import React, {useState, useRef} from 'react';
import '@site/src/css/AutoImage.css';

const AutoImage = ({src}) => {
    const imageRef = useRef(null);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const toggleFullScreen = () => setIsFullScreen(!isFullScreen);

    const handleMouseWheel = (event) => {
        if (isFullScreen) {
            toggleFullScreen(); // 在全屏状态下触发点击事件，退出全屏模式
        }
    };

    const calculateTransform = () => {
        if (imageRef.current && isFullScreen) { // 确保引用已经创建并且非全屏状态
            const rect = imageRef.current.getBoundingClientRect();
            const offsetX = window.innerWidth / 2 - (rect.left + rect.right) / 2;
            const offsetY = window.innerHeight / 2 - (rect.top + rect.bottom) / 2;
            const scaleX = window.innerWidth / rect.width;
            const scaleY = window.innerHeight / rect.height;
            const scale = Math.min(scaleX, scaleY);
            return `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
        }
        return 'none';
    };

    return (<>
        <div
            className={isFullScreen ? 'image-bg fullscreen' : 'image-bg'}
            onWheel={handleMouseWheel}
            onClick={toggleFullScreen}
        >
        </div>
        <img
            src={src}
            className={`image`}
            style={isFullScreen ? {
                transform: calculateTransform(), cursor: 'zoom-out', zIndex: '9999'
            } : {}}
            onClick={toggleFullScreen}
            ref={imageRef}
            alt="Image"
        />
    </>);
};

export default AutoImage;
