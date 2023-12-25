<script>
  
  import { onMount } from 'svelte';
  import { createForm } from "svelte-forms-lib";
  import * as yup from "yup";

  let grecaptchaclient;
  let isRecaptchaValid = false;
  let isFormEmpty = false;
  let grecaptchaLoaded = false;
  
  onMount(() => {
    const checkRecaptcha = setInterval(() => {
      if (window.grecaptcha && window.grecaptcha.ready) {
        window.grecaptcha.ready(() => {
          grecaptchaclient = grecaptcha.render('recaptchabox', {
            'sitekey': import.meta.env.VITE_RECAPTCHA_SITE_KEY,
            'size': 'normal',
            'callback': () => {
              isRecaptchaValid = grecaptcha.getResponse(grecaptchaclient) !== '';
            }
          });
          clearInterval(checkRecaptcha);
        });
        grecaptchaLoaded = true;
      }
    }, 100); // Check every 100ms
  });


  const sendForm = async ({name, email, message}) => {
    const token = await grecaptcha.getResponse(grecaptchaclient);
    await fetch('/api/contacts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, message, recaptcha: token })
    })
    .catch(async error => {
      console.error('Error:', await error)
    });
  }

  
  const {
    // observables state
    form,
    errors,
    state,
    touched,
    isValid,
    isSubmitting,
    isValidating,
    // handlers
    handleBlur,
    handleChange,
    handleSubmit
  } = createForm({
    initialValues: {
      name: "",
      email: "",
      message: ""
    },
    validationSchema: yup.object().shape({
      name: yup.string().required(),
      email: yup
        .string()
        .email()
        .required(),
      message: yup.string().required()
    }),
    onSubmit: values => {
      return sendForm(values).catch((e) => {
        alert(e);
      })
    }
  });

  const updateDirtyState = () => {
    isFormEmpty = $form.name === "" ||
                  $form.email === ""||
                  $form.message === "";
  };

  $: updateDirtyState();

</script>

<svelte:head>
<script src="https://www.google.com/recaptcha/api.js" async defer>
</script>
</svelte:head>

<form class="p-4 bg-base-100 sm:w-full md:w-1/2 lg:w-2/5" class:valid={$isValid && isRecaptchaValid} on:submit={handleSubmit}>
  <div class="form-control  py-2">
    <label for="name" class="label">
      <span class="label-text text-secondary">Name</span>
    </label>
    <input 
      id="name" class="input input-bordered input-secondary rounded-none"  name="name" type="text" on:keyup={handleChange} on:change={updateDirtyState} required/>
    {#if $errors.name && $touched.name}
      <small class="text-error">{$errors.name}</small>
    {/if}
  </div>
  <div class="form-control  py-2">
    <label for="email" class="label">
      <span class="label-text text-secondary">Email</span>
    </label>
    <input id="email" class="input input-bordered input-secondary rounded-none" name="email" type="email" on:keyup={handleChange} on:change={updateDirtyState} required/>
    {#if $errors.email && $touched.email}
      <small class="text-error">{$errors.email}</small>
    {/if}
  </div>
  <div class="form-control py-2">
    <label for="message" class="label">
      <span class="label-text text-secondary">Message</span>
    </label>
    <textarea id="message" class="textarea textarea-bordered textarea-secondary rounded-none h-40" name="message" type="textarea" on:keyup={handleChange} on:change={updateDirtyState} required></textarea>
    {#if $errors.message && $touched.message}
      <small class="text-error">{$errors.message}</small>
    {/if}
  </div>
  <div id="recaptchabox" class="py-4"></div>
  <button type="submit" class="submit-button px-10 py-2 border-2" disabled={!isRecaptchaValid || !$isValid || isFormEmpty}>Submit</button>
</form>




<style>
  .submit-button:valid {
    @apply text-secondary bg-primary border-secondary;
  }
  .submit-button:valid:hover{
    @apply text-primary bg-accent border-accent;
  }
  .submit-button:disabled {
    background: grey;
  }
</style>


