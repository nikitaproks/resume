<script>
  export let item;
  let flipped=false;

  function handleClick() {
    flipped = !flipped;
  }
</script>
  
  

<div class="card">
    <div class="card-inner border-2 border-accent {flipped==true ? 'card-flipped': ''}" on:click={handleClick}>
      <div class="card-front bg-primary text-secondary p-4">
        <h3>{item.category}</h3>
      </div>
      <div class="card-back bg-accent text-secondary text-center p-4">
        <p>{item.examples}</p>
      </div>
    </div>
</div>


  <style>
    .card {
      perspective: 1000px;
      min-height: 100px;
    }
  
    .card-inner {
      position: relative;
      width: 100%;
      height: 100%;
      transition: transform 0.8s;
      transform-style: preserve-3d;
    }
  
    .card-flipped {
      transform: rotateY(180deg);
    }
  
    .card-front, .card-back {
      position: absolute;
      width: 100%;
      height: 100%;
      backface-visibility: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  
    .card-back {
      transform: rotateY(180deg);
    }
  </style>